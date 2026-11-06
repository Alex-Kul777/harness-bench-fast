#!/usr/bin/env python3
"""Generate docs/fork.html + docs/fork-home-results.json — the single fork page.

One page with three suites (Shot List 52 / Light 391 / Medium 80), each a table
with the unified canonical schema:

    Harness · Profile · Model · Result · % · Time · Steps · Tokens (cost) · Version · Source

Our rows are read from the run JSONs (checkout ``results/`` first, then
``../results/``; first name wins). Upstream comparison rows are attached where a
machine-readable source exists (Light: ``docs/leaderboard-results.json``).
``Version`` = task-set version for our rows, ``source_version`` for upstream.

Usage:
    python3 scripts/build_fork_home.py            # write JSON + HTML
    python3 scripts/build_fork_home.py --check    # exit 1 if outputs are stale
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
OUT_JSON = DOCS / "fork-home-results.json"
OUT_HTML = DOCS / "fork.html"
LEADERBOARD = DOCS / "leaderboard-results.json"
MEDIUM_JSON = DOCS / "fork-medium90-results.json"

GENERATED_BY = "scripts/build_fork_home.py"
RESULT_DIRS = [REPO_ROOT / "results", REPO_ROOT.parent / "results"]
DASH = "\u2014"
RUB = "\u20bd"

HARNESS_PREFIXES = (
    ("opencode_", "opencode"), ("openclaw_", "OpenClaw"), ("hermes_", "Hermes"),
    ("pi_", "Pi"), ("oc_", "OpenClaw"),
)
MODEL_TOKENS = (
    ("ds41flash", "DeepSeek-V4.1-Flash"), ("glm53", "GLM-5.3"), ("glm52", "GLM-5.2"),
    ("qwen36", "Qwen3.6-35B-A3B"), ("oss120b", "GPT-OSS-120B"),
)
PROFILE_RULES = (("thinking_off", "thinking: off"), ("mcpoff", "MCP off"))
EXCLUDE = ("part2", "rerun", "smoke", "sample", "diag", "pilot")

# Our Light (391) runs — explicit allow-list (mirrors scripts/build_fork_light.py).
OURS_LIGHT = [
    ("Hermes", "MCP off", "GLM-5.2", "results/hermes_full_391.json"),
    ("Pi", "high", "GLM-5.2", "results/glm52_full_391.json"),
    ("OpenClaw", "", "GLM-5.2", "results/oc_full_391.json"),
]


def _collect() -> dict[str, Path]:
    seen: dict[str, Path] = {}
    for d in RESULT_DIRS:
        if d.is_dir():
            for p in sorted(d.glob("*.json")):
                seen.setdefault(p.name, p)
    return seen


def _harness(stem: str) -> str:
    for pre, h in HARNESS_PREFIXES:
        if stem.startswith(pre):
            return h
    return DASH


def _model(stem: str) -> str:
    for tok, m in MODEL_TOKENS:
        if tok in stem:
            return m
    return DASH


def _profile(stem: str) -> str:
    low = stem.lower()
    for tok, lab in PROFILE_RULES:
        if tok in low:
            return lab
    return ""


def _fmt_int(n) -> str:
    return DASH if n in (None, "") else f"{int(round(n)):,}".replace(",", " ")


def _fmt_pct(rate) -> str:
    return DASH if rate is None else f"{rate * 100:.1f}%"


def _fmt_min(secs) -> str:
    return DASH if secs is None else f"{float(secs) / 60:.1f}m"


def _fmt_cost(tokens, cost) -> str:
    tok = _fmt_int(tokens)
    if cost:
        return f"{tok} ({float(cost):,.0f}".replace(",", " ") + f"{RUB})"
    return tok


def _row(harness, profile, model, passed, total, rate, secs, steps, tokens, cost, version, source, url=None) -> dict:
    return {
        "harness": harness or DASH, "profile": profile or DASH, "model": model or DASH,
        "result": f"{int(passed)}/{int(total)}" if passed is not None and total else DASH,
        "pct": _fmt_pct(rate), "time": _fmt_min(secs), "steps": _fmt_int(steps),
        "tokens_cost": _fmt_cost(tokens, cost), "version": version or DASH,
        "source": source, "url": url,
    }


def _from_summary_file(harness, profile, model, path: Path, source="ours", url=None) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    s = d.get("summary") or {}
    rate = s.get("pass_rate")
    if rate is None and s.get("passed") is not None and s.get("total"):
        rate = s["passed"] / s["total"]
    return _row(harness, profile, model, s.get("passed", d.get("passed")), s.get("total", d.get("total")),
                rate, s.get("total_seconds"), s.get("total_steps", d.get("steps")),
                s.get("total_tokens", d.get("tokens")), s.get("estimated_cost_rub"),
                d.get("task_set_version"), source, url)


def ours_shotlist() -> list[dict]:
    out = []
    for name, path in _collect().items():
        if "_shotlist_" not in name:
            continue
        low = name.lower()
        if any(k in low for k in EXCLUDE):
            continue
        stem = path.stem
        url = "https://github.com/Alex-Kul777/harness-bench-fast/blob/main/results/" + name
        out.append(_from_summary_file(_harness(stem), _profile(stem), _model(stem), path, "ours", url))
    out.sort(key=lambda r: -_pct_val(r["pct"]))
    return out


def ours_light() -> list[dict]:
    out = []
    for harness, profile, model, rel in OURS_LIGHT:
        path = None
        for base in RESULT_DIRS:
            cand = base / rel.split("results/", 1)[-1]
            if cand.exists():
                path = cand
                break
        if path is None:
            raise SystemExit(f"missing light source: {rel}")
        url = "https://github.com/Alex-Kul777/harness-bench-fast/blob/main/" + rel
        out.append(_from_summary_file(harness, profile, model, path, "ours", url))
    return out


def ours_medium() -> list[dict]:
    if not MEDIUM_JSON.exists():
        return []
    d = json.loads(MEDIUM_JSON.read_text(encoding="utf-8"))
    ver = d.get("task_set_version")
    out = []
    for r in d.get("rows", []):
        suites = r.get("suites") or {}
        passed = sum((s.get("passed") or 0) for s in suites.values())
        total = sum((s.get("total") or 0) for s in suites.values())
        u = r.get("usage") or {}
        url = "https://github.com/Alex-Kul777/harness-bench-fast/blob/main/docs/" + (r.get("details_url") or "")
        out.append(_row(r.get("harness"), r.get("profile"), r.get("model"), passed, total,
                        (passed / total) if total else None, u.get("seconds"), u.get("steps"),
                        u.get("tokens"), u.get("cost_rub"), ver, "ours", url))
    return out


def upstream_light() -> list[dict]:
    if not LEADERBOARD.exists():
        return []
    d = json.loads(LEADERBOARD.read_text(encoding="utf-8"))
    out = []
    for r in d.get("rows", []):
        lt = r.get("light")
        if not lt:
            continue
        out.append(_row(r.get("harness"), "", r.get("model"), lt.get("passed"), lt.get("total"),
                        (lt["passed"] / lt["total"]) if lt.get("total") else None,
                        None, None, None, None, r.get("source_version"), "upstream"))
    out.sort(key=lambda r: -_pct_val(r["pct"]))
    return out


def _pct_val(s: str) -> float:
    try:
        return float(str(s).rstrip("%"))
    except ValueError:
        return -1.0


def build() -> dict:
    return {
        "generated_by": GENERATED_BY,
        "id": "fork-home",
        "version_semantics": "ours: task-set version · upstream: source_version",
        "suites": [
            {"key": "shotlist", "label": "Shot List (52)", "tasks": 52,
             "ours": ours_shotlist(), "upstream": []},
            {"key": "light", "label": "Light (391)", "tasks": 391,
             "ours": ours_light(), "upstream": upstream_light()},
            {"key": "medium", "label": "Medium (80)", "tasks": 80,
             "ours": ours_medium(), "upstream": []},
        ],
    }


def _rows_html(rows: list[dict]) -> str:
    tr = []
    for r in rows:
        src = html.escape(r["source"])
        if r.get("url"):
            src = f'<a href="{html.escape(r["url"])}">{src}</a>'
        tr.append(
            "<tr>"
            f"<td>{html.escape(r['harness'])}</td>"
            f"<td>{html.escape(r['profile'])}</td>"
            f"<td>{html.escape(r['model'])}</td>"
            f'<td class="numeric">{html.escape(r["result"])}</td>'
            f'<td class="numeric">{html.escape(r["pct"])}</td>'
            f'<td class="numeric">{html.escape(r["time"])}</td>'
            f'<td class="numeric">{html.escape(r["steps"])}</td>'
            f'<td class="numeric">{html.escape(r["tokens_cost"])}</td>'
            f"<td>{html.escape(r['version'])}</td>"
            f"<td>{src}</td>"
            "</tr>"
        )
    return "\n".join(tr) or f'<tr><td colspan="10">{DASH}</td></tr>'


HEAD = """<tr>
  <th scope="col">Harness</th><th scope="col">Profile</th><th scope="col">Model</th>
  <th scope="col" class="numeric">Result</th><th scope="col" class="numeric">%</th>
  <th scope="col" class="numeric">Time</th><th scope="col" class="numeric">Steps</th>
  <th scope="col" class="numeric">Tokens (cost)</th><th scope="col">Version</th><th scope="col">Source</th>
</tr>"""

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Fork results for harness_bench_fast: our Shot List (52), Light (391) and Medium (80) runs, with upstream comparison. Mechanically verified.">
  <title>harness_bench_fast · Fork results</title>
  <link rel="stylesheet" href="landing.css">
</head>
<body>
  <header>
    <a class="brand" href="index.html">harness_bench_fast<span class="brand-dot">.</span></a>
    <nav aria-label="Primary"><a href="../FORK.md">Fork index</a> <a href="#shotlist">Shot List (52)</a> <a href="#light">Light (391)</a> <a href="#medium">Medium (80)</a> <a href="fork-sample.html">Capability sample (20)</a></nav>
  </header>
  <main>
    <section class="intro">
      <p class="eyebrow">Fork results · our runs</p>
      <h1>Our runs.<br>Three suites, one page.</h1>
      <p class="lead">Our Pi / OpenClaw / Hermes runs on the frozen Shot List (52), Light (391) and Medium (80) suites. Real tasks, mechanically verified.</p>
    </section>
__SECTIONS__
    <p class="fine-print">No LLM judge. Every task is checked mechanically. A dash means no measurement yet, not a failure. <code>Version</code> = task-set version for our runs, upstream <code>source_version</code> for upstream rows. <a href="../FORK.md">Fork index</a> · <a href="fork-results.md">Fork tables →</a></p>
  </main>
  <footer><span>No LLM judge. Every task is checked mechanically.</span><a href="../FORK.md">Fork index →</a></footer>
</body>
</html>
"""


def _section(suite: dict) -> str:
    parts = [f'    <section id="{suite["key"]}" aria-label="{html.escape(suite["label"])}">',
             f'      <h2>{html.escape(suite["label"])}</h2>',
             f'      <p class="coverage-note">Tasks {suite["tasks"]}. Our runs, plus upstream comparison where a machine-readable source exists.</p>',
             '      <div class="table-wrap">',
             '        <table class="leaderboard-table"><thead>' + HEAD + '</thead><tbody>',
             _rows_html(suite["ours"])]
    if suite["upstream"]:
        parts.append('        </tbody><tbody>')
        parts.append('          <tr><td colspan="10"><strong>Upstream comparison</strong></td></tr>')
        parts.append(_rows_html(suite["upstream"]))
    parts += ['        </tbody></table>', '      </div>', '    </section>']
    return "\n".join(parts)


def render_html(data: dict) -> str:
    return PAGE.replace("__SECTIONS__", "\n".join(_section(s) for s in data["suites"]))


def main(argv: list[str]) -> int:
    data = build()
    blob = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    page = render_html(data)
    if "--check" in argv:
        stale = [p.name for p, want in ((OUT_JSON, blob), (OUT_HTML, page))
                 if not p.exists() or p.read_text(encoding="utf-8") != want]
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
        print("up to date")
        return 0
    OUT_JSON.write_text(blob, encoding="utf-8")
    OUT_HTML.write_text(page, encoding="utf-8")
    counts = ", ".join(f"{s['label']}: {len(s['ours'])}+{len(s['upstream'])}" for s in data["suites"])
    print(f"wrote {OUT_JSON.name} + {OUT_HTML.name} ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
