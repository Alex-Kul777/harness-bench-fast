#!/usr/bin/env python3
"""Generate docs/fork-light.html + docs/fork-light-results.json.

Publishes the fork's own full **Light (391)** runs (tasks 1-391) as a dedicated
view, together with the upstream Light leaderboard rows (read-only) for
comparison.

Our rows come from an explicit allow-list (the Light runs live in
``<repo>/results`` or one level up in ``<repo>/../results``); the upstream rows
come from ``docs/leaderboard-results.json``. Every dynamic value is
HTML-escaped.

Usage:
    python3 scripts/build_fork_light.py            # write JSON + HTML
    python3 scripts/build_fork_light.py --check    # exit 1 if outputs are stale
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
OUT_JSON = DOCS / "fork-light-results.json"
OUT_HTML = DOCS / "fork-light.html"
LEADERBOARD = DOCS / "leaderboard-results.json"

GENERATED_BY = "scripts/build_fork_light.py"
SUITE = {"key": "light", "label": "Light (391)", "first": 1, "last": 391, "tasks": 391}

# Checkout's own results win on a name clash; the shared store lives one level up.
RESULT_DIRS = [REPO_ROOT / "results", REPO_ROOT.parent / "results"]

BLOB = "https://github.com/Alex-Kul777/harness-bench-fast/blob/main/"
DASH = "\u2014"
RUB = "\u20bd"

# Explicit allow-list: (harness, profile, model, relative source file).
# Fork rule: raw runs are runs/*_v016.json; the *current* summary comes from
# results/ — so Pi means results/glm52_full_391.json, not the raw runs file.
OURS = [
    ("Hermes", "MCP off", "GLM-5.2", "results/hermes_full_391.json"),
    ("Pi", "high", "GLM-5.2", "results/glm52_full_391.json"),
    ("OpenClaw", "", "GLM-5.2", "results/oc_full_391.json"),
]


def _resolve(rel: str) -> Path | None:
    for base in RESULT_DIRS:
        p = base / rel.split("results/", 1)[-1]
        if p.exists():
            return p
    p = REPO_ROOT / rel
    return p if p.exists() else None


def _our_row(harness: str, profile: str, model: str, rel: str) -> dict:
    path = _resolve(rel)
    if path is None:
        raise SystemExit(f"missing Light source: {rel}")
    d = json.load(open(path, encoding="utf-8"))
    s = d.get("summary") or {}
    passed = s.get("passed", d.get("passed"))
    total = s.get("total", d.get("total"))
    rate = s.get("pass_rate", d.get("pass_rate"))
    if rate is None and passed is not None and total:
        rate = passed / total
    secs = s.get("total_seconds")
    steps = s.get("total_steps", d.get("steps"))
    tokens = s.get("total_tokens", d.get("tokens"))
    cost = s.get("estimated_cost_rub")
    return {
        "harness": harness,
        "profile": profile,
        "model": model,
        "passed": passed,
        "total": total,
        "pass_rate": rate,
        "minutes": round(secs / 60.0, 1) if secs else None,
        "steps": steps,
        "tokens": tokens,
        "cost_rub": cost,
        "source": rel,
        "url": BLOB + rel,
    }


def _upstream_rows() -> list[dict]:
    d = json.load(open(LEADERBOARD, encoding="utf-8"))
    out = []
    for r in d.get("rows", []):
        lt = r.get("light")
        if not lt:
            continue
        out.append({
            "harness": r.get("harness") or DASH,
            "model": r.get("model") or DASH,
            "passed": lt.get("passed"),
            "total": lt.get("total"),
            "source_version": r.get("source_version") or DASH,
        })
    out.sort(key=lambda x: (-(x["passed"] or 0), x["harness"].lower()))
    return out


def build() -> dict:
    return {
        "generated_by": GENERATED_BY,
        "id": "fork-light",
        "suite": SUITE,
        "config": {"harness": "Pi", "model": "GLM-5.2"},
        "ours": [_our_row(*o) for o in OURS],
        "upstream": _upstream_rows(),
    }


def _fmt_int(n) -> str:
    if n in (None, ""):
        return DASH
    return f"{int(round(n)):,}".replace(",", " ")


def _fmt_pct(rate) -> str:
    return DASH if rate is None else f"{rate * 100:.1f}%"


def _fmt_min(m) -> str:
    return DASH if m is None else f"{m}m"


def _fmt_cost(tokens, cost) -> str:
    tok = _fmt_int(tokens)
    if cost:
        return f"{tok} ({cost:g}{RUB})"
    return tok


def _our_rows_html(rows: list[dict]) -> str:
    tr = []
    for r in rows:
        result = f"{r['passed']}/{r['total']}" if r["passed"] is not None else DASH
        tr.append(
            "<tr>"
            f"<td>{html.escape(r['harness'])}</td>"
            f"<td>{html.escape(r['profile']) or DASH}</td>"
            f"<td>{html.escape(r['model'])}</td>"
            f'<td class="numeric">{result}</td>'
            f'<td class="numeric">{_fmt_pct(r["pass_rate"])}</td>'
            f'<td class="numeric">{_fmt_min(r["minutes"])}</td>'
            f'<td class="numeric">{_fmt_int(r["steps"])}</td>'
            f'<td class="numeric">{_fmt_cost(r["tokens"], r["cost_rub"])}</td>'
            f'<td><a href="{html.escape(r["url"])}">JSON</a></td>'
            "</tr>"
        )
    return "\n".join(tr)


def _upstream_rows_html(rows: list[dict]) -> str:
    tr = []
    for i, r in enumerate(rows, 1):
        result = f"{r['passed']}/{r['total']}"
        rate = (r["passed"] / r["total"]) if r["total"] else None
        tr.append(
            "<tr>"
            f'<td class="numeric">{i}</td>'
            f"<td>{html.escape(str(r['harness']))}</td>"
            f"<td>{html.escape(str(r['model']))}</td>"
            f'<td class="numeric">{html.escape(result)}</td>'
            f'<td class="numeric">{_fmt_pct(rate)}</td>'
            f"<td>{html.escape(str(r['source_version']))}</td>"
            "</tr>"
        )
    return "\n".join(tr)


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Fork results for harness_bench_fast Light (tasks 1-391): our full runs plus the upstream Light leaderboard for comparison. Mechanically verified.">
  <title>harness_bench_fast · Fork Light (391)</title>
  <link rel="stylesheet" href="landing.css">
</head>
<body>
  <header>
    <a class="brand" href="index.html">harness_bench_fast<span class="brand-dot">.</span></a>
    <nav aria-label="Primary"><a href="../FORK.md">Fork index</a> <a href="fork-medium90.html">Medium 80</a> <a href="fork-sample.html">Capability sample (20)</a></nav>
  </header>
  <main>
    <section class="intro">
      <p class="eyebrow">Fork results · Light · tasks 1–391 (frozen)</p>
      <h1>Light (391)<br>our full runs.</h1>
      <p class="lead">Our Hermes / Pi / OpenClaw runs on the frozen 391-task Light suite, plus the upstream Light leaderboard for comparison. Real tasks, mechanically verified.</p>
    </section>

    <section aria-label="Our Light runs">
      <h2>Our full Light runs (391)</h2>
      <p class="coverage-note">Full runs of the frozen Light suite (tasks 1–391). Values are read from the run JSONs; a dash means no usable total for that column.</p>
      <div class="table-wrap">
        <table class="leaderboard-table"><thead><tr>
          <th scope="col">Harness</th><th scope="col">Profile</th><th scope="col">Model</th>
          <th scope="col" class="numeric">Result</th><th scope="col" class="numeric">%</th>
          <th scope="col" class="numeric">Time</th><th scope="col" class="numeric">Steps</th>
          <th scope="col" class="numeric">Tokens (cost)</th><th scope="col">Source</th>
        </tr></thead><tbody>
__OURS__
        </tbody></table>
      </div>

      <h2>Upstream Light (391) — comparison</h2>
      <p class="coverage-note">Upstream Light leaderboard rows (read-only, from <code>leaderboard-results.json</code>), sorted by passed tasks. A comparison reference — not our runs.</p>
      <div class="table-wrap">
        <table class="leaderboard-table"><thead><tr>
          <th scope="col" class="numeric">#</th><th scope="col">Harness</th><th scope="col">Model</th>
          <th scope="col" class="numeric">Result</th><th scope="col" class="numeric">%</th>
          <th scope="col">Version</th>
        </tr></thead><tbody>
__UPSTREAM__
        </tbody></table>
      </div>

      <p class="fine-print">No LLM judge. Every task is checked mechanically. <a href="../FORK.md">Fork index</a> · <a href="fork-medium90.html">Medium 80</a> · <a href="fork-results.md">Fork tables →</a></p>
    </section>
  </main>
  <footer><span>No LLM judge. Every task is checked mechanically.</span><a href="../FORK.md">Fork index →</a></footer>
</body>
</html>
"""


def render_html(data: dict) -> str:
    return (
        PAGE
        .replace("__OURS__", _our_rows_html(data["ours"]))
        .replace("__UPSTREAM__", _upstream_rows_html(data["upstream"]))
    )


def main(argv: list[str]) -> int:
    data = build()
    blob = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    page = render_html(data)
    if "--check" in argv:
        stale = []
        if not OUT_JSON.exists() or OUT_JSON.read_text(encoding="utf-8") != blob:
            stale.append(OUT_JSON.name)
        if not OUT_HTML.exists() or OUT_HTML.read_text(encoding="utf-8") != page:
            stale.append(OUT_HTML.name)
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
        print("up to date")
        return 0
    OUT_JSON.write_text(blob, encoding="utf-8")
    OUT_HTML.write_text(page, encoding="utf-8")
    print(f"wrote {OUT_JSON.name} ({len(data['ours'])} ours, {len(data['upstream'])} upstream) + {OUT_HTML.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
