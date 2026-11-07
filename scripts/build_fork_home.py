#!/usr/bin/env python3
"""Generate docs/fork.html (tabbed) + docs/fork-home-results.json — the single fork page.

One page, one dataset, three tabs: Shot List (52) / Light (391) / Medium (80).
Each suite table uses exactly the canonical nine columns:

    Harness · Profile · Model · Result · % · Time · Steps · Tokens (cost) · Version

Ours vs upstream are separated by group header rows (not a column). The Medium
wave breakdown (long / reflect / feasibility) lives in a collapsible <details>
block so the main table keeps the nine columns. Tab state follows the URL hash
(#shotlist / #light / #medium), so the old redirect stubs keep working.

Usage:
    python3 scripts/build_fork_home.py            # write JSON + HTML
    python3 scripts/build_fork_home.py --check    # exit 1 if outputs are stale
"""
from __future__ import annotations

import contextlib
import html
import json
import re
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
    ("ds41flash", "DeepSeek-V4.1-Flash"), ("gigachat3pro", "GigaChat 3 Pro"),
    ("glm53", "GLM-5.3"), ("glm52", "GLM-5.2"),
    ("qwen36", "Qwen3.6-35B-A3B"), ("oss120b", "GPT-OSS-120B"),
)

# Upstream writes the reasoning level inside the Model cell, e.g.
# "Claude Haiku 5.5 (OpenRouter) (default)". We mirror that by surfacing our
# profile's reasoning token: "thinking: off" -> "(thinking: off)", "high" -> "(high)".
# Non-reasoning profiles (e.g. "MCP off") get no suffix.
REASON_LEVELS = ("high", "medium", "low", "minimal")


def _reasoning_suffix(profile):
    p = (profile or "").strip()
    if not p or p == DASH:
        return ""
    if p.startswith("thinking") or p in REASON_LEVELS:
        return f"({p})"
    return ""


def _with_reasoning(model, profile):
    suffix = _reasoning_suffix(profile)
    return f"{model} {suffix}".strip() if suffix else model


def _harness_version(data):
    """Harness version, if the run artifact records it (upstream writes
    'pi-mono 0.73.1'; our artifacts currently do not record it)."""
    for k in ("harness_version", "openclaw_version", "cli_version", "runner_version"):
        v = (data or {}).get(k)
        if v:
            return str(v)
    return None


def _with_version(harness, version):
    return f"{harness} {version}" if version else harness
PROFILE_RULES = (("thinking_off", "thinking: off"), ("mcpoff", "MCP off"))
EXCLUDE = ("part2", "rerun", "smoke", "sample", "diag", "pilot")

OURS_LIGHT = [
    ("Hermes", "MCP off", "GLM-5.2", "results/hermes_full_391.json"),
    ("Pi", "high", "GLM-5.2", "results/glm52_full_391.json"),
    ("OpenClaw", "", "GLM-5.2", "results/oc_full_391.json"),
]

# (detail_filename, suite_key, row, run_data) collected while building; written on run.
_DETAIL_JOBS: list = []
WAVE_LABELS = (("long", "Long"), ("reflect", "Reflect"), ("feasibility", "Feasibility"))

# Harnesses that are OUR runs; anything else in the README shot-list table is upstream.
UPSTREAM_OURS = {"pi", "openclaw", "hermes"}
README = REPO_ROOT / "README.md"


def _collect() -> dict[str, Path]:
    seen: dict[str, Path] = {}
    for d in RESULT_DIRS:
        if d.is_dir():
            for p in sorted(d.glob("*.json")):
                seen.setdefault(p.name, p)
    return seen


def _harness(stem):
    for pre, h in HARNESS_PREFIXES:
        if stem.startswith(pre):
            return h
    return DASH


def _model(stem):
    for tok, m in MODEL_TOKENS:
        if tok in stem:
            return m
    if "thinking_off" in stem.lower():
        return "GLM-5.2"
    return DASH


def _profile(stem):
    low = stem.lower()
    for tok, lab in PROFILE_RULES:
        if tok in low:
            return lab
    return ""


def _fmt_int(n):
    return DASH if n in (None, "") else f"{int(round(n)):,}".replace(",", " ")


def _fmt_pct(rate):
    return DASH if rate is None else f"{rate * 100:.1f}%"


def _fmt_min(secs):
    return DASH if secs is None else f"{float(secs) / 60:.1f}m"


def _fmt_cost(tokens, cost):
    tok = _fmt_int(tokens)
    if cost:
        return f"{tok} ({float(cost):,.0f}".replace(",", " ") + f"{RUB})"
    return tok


_SESSION_RE = re.compile(r"(\d{8})_")
_NAME_DATE_RE = re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)")


def _with_date(profile, date):
    """Append a run date to a profile label, README-style: 'thinking: off (2026-11-04)'."""
    if not date:
        return profile
    return f"{(profile or DASH)} ({date})"


def _date_from_name(name):
    m = _NAME_DATE_RE.search(name or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def _date_from_sessions(data):
    dates = []
    for key in ("tasks", "results"):
        for t in (data.get(key) or []):
            if not isinstance(t, dict):
                continue
            m = _SESSION_RE.match(t.get("session_id") or "")
            if m:
                dates.append(m.group(1))
    if not dates:
        return None
    d = min(dates)
    return f"{d[0:4]}-{d[4:6]}-{d[6:8]}"


def _readme_our_dates():
    """Map (harness, model) -> [(profile_text, date)] from the README shot-list table (our rows)."""
    out = {}
    if not README.exists():
        return out
    m = re.search(r"## Shot List Leaderboard \(52 tasks\)(.*?)(?=\n## )", README.read_text(encoding="utf-8"), re.S)
    if not m:
        return out
    for line in m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8 or cells[0].lower() not in UPSTREAM_OURS:
            continue
        dm = re.search(r"\((\d{4}-\d{2}-\d{2})\)", cells[1])
        out.setdefault((cells[0].lower(), cells[2].lower()), []).append((cells[1], dm.group(1) if dm else None))
    return out


def _readme_date_for(map_, harness, model, profile):
    cands = map_.get(((harness or "").lower(), (model or "").lower()), [])
    if profile:
        for text, date in cands:
            if profile.lower() in text.lower() and date:
                return date
    for _, date in cands:
        if date:
            return date
    return None


def _date_from_source_files(names):
    dates = []
    for n in names or []:
        dates.append(_date_from_name(n))
        for base in RESULT_DIRS:
            p = base / n
            if p.exists():
                with contextlib.suppress(OSError, json.JSONDecodeError):
                    dates.append(_date_from_sessions(json.loads(p.read_text(encoding="utf-8"))))
                break
    dates = [d for d in dates if d]
    return min(dates) if dates else None


def _row(harness, profile, model, passed, total, rate, secs, steps, tokens, cost, version, source, waves=None, detail=None):
    return {
        "harness": harness or DASH, "profile": profile or DASH, "model": model or DASH,
        "result": f"{int(passed)}/{int(total)}" if passed is not None and total else DASH,
        "pct": _fmt_pct(rate), "time": _fmt_min(secs), "steps": _fmt_int(steps),
        "tokens_cost": _fmt_cost(tokens, cost), "version": version or DASH,
        "source": source, "waves": waves, "detail": detail,
    }


def _from_summary_file(harness, profile, model, path: Path, source="ours", date_hint=None, suite=None, detail=None):
    d = json.loads(path.read_text(encoding="utf-8"))
    s = d.get("summary") or {}
    rate = s.get("pass_rate")
    if rate is None and s.get("passed") is not None and s.get("total"):
        rate = s["passed"] / s["total"]
    date = _date_from_sessions(d) or _date_from_name(path.name) or date_hint
    row = _row(_with_version(harness, _harness_version(d)), _with_date(profile, date),
               _with_reasoning(model, profile),
               s.get("passed", d.get("passed")), s.get("total", d.get("total")),
               rate, s.get("total_seconds"), s.get("total_steps", d.get("steps")),
               s.get("total_tokens", d.get("tokens")), s.get("estimated_cost_rub"),
               d.get("task_set_version"), source, detail=detail)
    if detail:
        _DETAIL_JOBS.append((detail, suite, row, d))
    return row


def ours_shotlist():
    out = []
    rmap = _readme_our_dates()
    for name, path in _collect().items():
        if "_shotlist_" not in name:
            continue
        low = name.lower()
        if any(k in low for k in EXCLUDE):
            continue
        stem = path.stem
        harness, profile, model = _harness(stem), _profile(stem), _model(stem)
        hint = _readme_date_for(rmap, harness, model, profile)
        out.append(_from_summary_file(harness, profile, model, path, date_hint=hint,
                                      suite="shotlist", detail=f"fork-detail-{path.stem}.html"))
    out.sort(key=lambda r: -_pct_val(r["pct"]))
    return out


def ours_light():
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
        out.append(_from_summary_file(harness, profile, model, path,
                                      suite="light", detail=f"fork-detail-{path.stem}.html"))
    return out


def ours_medium():
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
        waves = {k: {"passed": (suites.get(k) or {}).get("passed"),
                     "total": (suites.get(k) or {}).get("total")} for k, _ in WAVE_LABELS}
        date = _date_from_source_files(r.get("sources"))
        out.append(_row(_with_version(r.get("harness"), _harness_version(r)),
                        _with_date(r.get("profile"), date),
                        _with_reasoning(r.get("model"), r.get("profile")),
                        passed, total, (passed / total) if total else None, u.get("seconds"),
                        u.get("steps"), u.get("tokens"), u.get("cost_rub"), ver, "ours", waves,
                        detail=r.get("details_url")))
    return out


def upstream_light():
    if not LEADERBOARD.exists():
        return []
    d = json.loads(LEADERBOARD.read_text(encoding="utf-8"))
    out = []
    for r in d.get("rows", []):
        lt = r.get("light")
        if not lt:
            continue
        out.append(_row(r.get("harness"), _with_date("", r.get("measurement_date")), r.get("model"),
                        lt.get("passed"), lt.get("total"),
                        (lt["passed"] / lt["total"]) if lt.get("total") else None,
                        None, None, None, None, r.get("source_version"), "upstream"))
    out.sort(key=lambda r: -_pct_val(r["pct"]))
    return out


def _pct_val(s):
    try:
        return float(str(s).rstrip("%"))
    except ValueError:
        return -1.0


def _norm_cell(s):
    """Tidy a raw markdown cell: bare dash -> em dash, strip space thousands."""
    s = (s or "").strip()
    if s in ("-", "\u2013", ""):
        return DASH
    return s.replace(",", " ")


def _raw_row(harness, profile, model, result, pct, time, steps, tokens_cost, version, source):
    return {"harness": harness or DASH, "profile": profile or DASH, "model": model or DASH,
            "result": result or DASH, "pct": pct or DASH, "time": time or DASH,
            "steps": steps or DASH, "tokens_cost": tokens_cost or DASH,
            "version": version or DASH, "source": source, "waves": None, "detail": None}


def upstream_shotlist():
    """Upstream rows of the fork README shot-list table (our harnesses excluded)."""
    if not README.exists():
        return []
    import re
    txt = README.read_text(encoding="utf-8")
    m = re.search(r"## Shot List Leaderboard \(52 tasks\)(.*?)(?=\n## )", txt, re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8 or cells[0].lower() == "harness" or set(cells[0]) <= set("-: "):
            continue
        if cells[0].lower() in UPSTREAM_OURS:
            continue
        out.append(_raw_row(cells[0], cells[1], cells[2], cells[3], cells[4],
                            _norm_cell(cells[5]), _norm_cell(cells[6]), _norm_cell(cells[7]),
                            DASH, "upstream"))
    return out


def upstream_medium():
    """Upstream Medium (80) rows from the published leaderboard."""
    if not LEADERBOARD.exists():
        return []
    d = json.loads(LEADERBOARD.read_text(encoding="utf-8"))
    out = []
    for r in d.get("rows", []):
        md = r.get("medium")
        if not md:
            continue
        out.append(_row(r.get("harness"), _with_date("", r.get("measurement_date")), r.get("model"),
                        md.get("passed"), md.get("total"),
                        (md["passed"] / md["total"]) if md.get("total") else None,
                        None, None, None, None, r.get("source_version"), "upstream"))
    out.sort(key=lambda x: -_pct_val(x["pct"]))
    return out


def build():
    return {
        "generated_by": GENERATED_BY,
        "id": "fork-home",
        "version_semantics": "ours: task-set version · upstream: source_version",
        "suites": [
            {"key": "shotlist", "label": "Shot List (52)", "tasks": 52, "ours": ours_shotlist(), "upstream": upstream_shotlist()},
            {"key": "light", "label": "Light (391)", "tasks": 391, "ours": ours_light(), "upstream": upstream_light()},
            {"key": "medium", "label": "Medium (80)", "tasks": 80, "ours": ours_medium(), "upstream": upstream_medium()},
        ],
    }


def _rows_html(rows):
    tr = []
    for r in rows:
        d = r.get("detail")
        attrs = f' class="detail-row" data-detail="{html.escape(d)}"' if d else ""
        harness = (f'<a href="{html.escape(d)}">{html.escape(r["harness"])}</a>'
                   if d else html.escape(r['harness']))
        tr.append(
            f"<tr{attrs}>"
            f"<td>{harness}</td>"
            f"<td>{html.escape(r['profile'])}</td>"
            f"<td>{html.escape(r['model'])}</td>"
            f'<td class="numeric">{html.escape(r["result"])}</td>'
            f'<td class="numeric">{html.escape(r["pct"])}</td>'
            f'<td class="numeric">{html.escape(r["time"])}</td>'
            f'<td class="numeric">{html.escape(r["steps"])}</td>'
            f'<td class="numeric">{html.escape(r["tokens_cost"])}</td>'
            f"<td>{html.escape(r['version'])}</td>"
            "</tr>"
        )
    return "\n".join(tr)


HEAD = """<tr>
  <th scope="col">Harness</th><th scope="col">Profile</th><th scope="col">Model</th>
  <th scope="col" class="numeric">Result</th><th scope="col" class="numeric">%</th>
  <th scope="col" class="numeric">Time</th><th scope="col" class="numeric">Steps</th>
  <th scope="col" class="numeric">Tokens (cost)</th><th scope="col">Version</th>
</tr>"""


def _table(rows, group_ours="Our runs", group_up="Upstream comparison"):
    parts = ['<table class="leaderboard-table"><thead>' + HEAD + '</thead><tbody>',
             f'<tr class="group"><td colspan="9"><strong>{group_ours}</strong></td></tr>',
             _rows_html(rows)]
    parts.append('</tbody></table>')
    return "\n".join(parts)


def _table_groups(ours, upstream):
    parts = ['<table class="leaderboard-table"><thead>' + HEAD + '</thead><tbody>',
             '<tr class="group"><td colspan="9"><strong>Our runs</strong></td></tr>',
             _rows_html(ours)]
    if upstream:
        parts.append('<tr class="group"><td colspan="9"><strong>Upstream comparison</strong></td></tr>')
        parts.append(_rows_html(upstream))
    parts.append('</tbody></table>')
    return "\n".join(parts)


def _waves_html(rows):
    body = []
    for r in rows:
        w = r.get("waves") or {}
        cells = []
        for k, _ in WAVE_LABELS:
            c = w.get(k) or {}
            p, t = c.get("passed"), c.get("total")
            cells.append(f'<td class="numeric">{f"{p}/{t}" if p is not None and t else DASH}</td>')
        body.append(f"<tr><td>{html.escape(r['harness'])} · {html.escape(r['model'])}</td>" + "".join(cells) + "</tr>")
    head = "".join(f'<th scope="col" class="numeric">{lab}</th>' for _, lab in WAVE_LABELS)
    return (
        '<details class="wave-breakdown"><summary>Wave breakdown (long / reflect / feasibility)</summary>'
        '<div class="table-wrap"><table class="leaderboard-table"><thead>'
        f'<tr><th scope="col">Configuration</th>{head}</tr></thead><tbody>'
        + "\n".join(body) + "</tbody></table></div></details>"
    )


def _panel(suite):
    key = suite["key"]
    inner = _table_groups(suite["ours"], suite["upstream"]) if suite["upstream"] else _table(suite["ours"])
    extra = _waves_html(suite["ours"]) if key == "medium" and suite["ours"] else ""
    return (
        f'      <section data-suite-panel="{key}" aria-label="{html.escape(suite["label"])}">\n'
        f'        <div class="table-wrap">{inner}</div>\n'
        + (extra + "\n" if extra else "")
        + "      </section>"
    )


STYLE = """<style>
  .suite-switch button[aria-pressed="true"]{font-weight:700;text-decoration:underline}
  tr.group td{background:rgba(127,127,127,.12);font-size:.92em}
  [data-suite-panel][hidden]{display:none}
  .wave-breakdown{margin-top:.6rem}
  tr[data-detail]{cursor:pointer}
  tr[data-detail]:hover td{background:rgba(127,127,127,.08)}
  .filters{display:flex;flex-wrap:wrap;gap:.8rem;align-items:center;margin:.9rem 0}
  .filters .search{display:flex;gap:.5rem;align-items:center}
  #row-count{font-size:.9em;opacity:.8}
</style>"""

SCRIPT = """<script>
(function(){
  var btns=[].slice.call(document.querySelectorAll('.suite-switch button'));
  var panels=[].slice.call(document.querySelectorAll('[data-suite-panel]'));
  var search=document.getElementById('search');
  var count=document.getElementById('row-count');
  var empty=document.getElementById('empty');
  function activePanel(){return document.querySelector('[data-suite-panel]:not([hidden])');}
  function applyFilter(){
    var panel=activePanel(); if(!panel) return;
    var tbody=panel.querySelector('.table-wrap table.leaderboard-table tbody');
    if(!tbody) return;
    var rows=[].slice.call(tbody.querySelectorAll('tr'));
    var q=(search.value||'').trim().toLocaleLowerCase();
    var shown=0, curGroup=null, groupHas=new Map();
    rows.forEach(function(r){
      if(r.classList.contains('group')){curGroup=r; groupHas.set(r,false); return;}
      var match=!q || r.textContent.toLocaleLowerCase().indexOf(q)>=0;
      r.hidden=!match;
      if(match){shown++; if(curGroup) groupHas.set(curGroup,true);}
    });
    rows.forEach(function(r){ if(r.classList.contains('group')) r.hidden=!groupHas.get(r); });
    count.textContent = q ? (shown+' match'+(shown===1?'':'es')) : (shown+' rows');
    empty.hidden = !(q && shown===0);
  }
  function activate(key){
    btns.forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.suite===key));});
    panels.forEach(function(p){p.hidden=(p.dataset.suitePanel!==key);});
    applyFilter();
  }
  function keyFromHash(){var h=(location.hash||'').replace('#','');
    var keys=btns.map(function(b){return b.dataset.suite;});
    return keys.indexOf(h)>=0?h:keys[0];}
  btns.forEach(function(b){b.addEventListener('click',function(){activate(b.dataset.suite);history.replaceState(null,'','#'+b.dataset.suite);});});
  window.addEventListener('hashchange',function(){activate(keyFromHash());});
  search.addEventListener('input',applyFilter);
  document.querySelectorAll('tr[data-detail]').forEach(function(tr){
    tr.addEventListener('click',function(e){
      if(e.target.closest('a')) return;
      location.href=tr.dataset.detail;
    });
  });
  activate(keyFromHash());
})();
</script>"""

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Fork results for harness_bench_fast: Shot List (52), Light (391) and Medium (80) in one tabbed page. Mechanically verified.">
  <title>harness_bench_fast · Fork results</title>
  <link rel="stylesheet" href="landing.css">
__STYLE__
</head>
<body>
  <header>
    <a class="brand" href="index.html">harness_bench_fast<span class="brand-dot">.</span></a>
    <nav aria-label="Primary"><a href="../FORK.md">Fork index</a> <a href="fork-sample.html">Capability sample (20)</a></nav>
  </header>
  <main>
    <section class="intro">
      <p class="eyebrow">Fork results · our runs</p>
      <h1>Our runs.<br>Three suites, one page.</h1>
      <p class="lead">Our Pi / OpenClaw / Hermes runs on the frozen Shot List (52), Light (391) and Medium (80) suites. Real tasks, mechanically verified.</p>
    </section>
    <div class="suite-switch" role="group" aria-label="Benchmark suite">
      <button type="button" data-suite="shotlist" aria-pressed="true"><strong>Shot List (52)</strong><span>stratified sample</span></button>
      <button type="button" data-suite="light" aria-pressed="false"><strong>Light (391)</strong><span>frozen suite</span></button>
      <button type="button" data-suite="medium" aria-pressed="false"><strong>Medium (80)</strong><span>long · reflect · feasibility</span></button>
    </div>
    <div class="filters">
      <label class="search">Search model or harness<input id="search" type="search" placeholder="e.g. Pi, OpenClaw, DeepSeek" autocomplete="off"></label>
      <span id="row-count" aria-live="polite"></span>
    </div>
__PANELS__
    <p id="empty" role="status" hidden>No rows match your search.</p>
    <p class="fine-print">No LLM judge. Every task is checked mechanically. A dash means no measurement yet, not a failure. <code>Version</code> = task-set version for our runs, upstream <code>source_version</code> for upstream rows. <a href="../FORK.md">Fork index</a> · <a href="fork-results.md">Fork tables →</a></p>
  </main>
  <footer><span>No LLM judge. Every task is checked mechanically.</span><a href="../FORK.md">Fork index →</a></footer>
__SCRIPT__
</body>
</html>
"""


def render_html(data):
    return (PAGE
            .replace("__STYLE__", STYLE)
            .replace("__PANELS__", "\n".join(_panel(s) for s in data["suites"]))
            .replace("__SCRIPT__", SCRIPT))


DETAIL_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <link rel="stylesheet" href="landing.css">
  <style>.msg pre{white-space:pre-wrap;word-break:break-word;max-height:280px;overflow:auto;margin:.3rem 0 0}</style>
</head>
<body>
  <header>
    <a class="brand" href="index.html">harness_bench_fast<span class="brand-dot">.</span></a>
    <nav aria-label="Primary"><a href="fork.html#__SUITE__">\u2190 Fork results</a></nav>
  </header>
  <main>
    <section class="intro">
      <p class="eyebrow">Fork run detail</p>
      <h1>__H1__</h1>
      <p class="lead">__META__</p>
    </section>
    <h2>Tasks (__N__)</h2>
    <div class="table-wrap">
      <table class="leaderboard-table"><thead><tr>
        <th scope="col" class="numeric">#</th><th scope="col">Task</th><th scope="col">Result</th>
        <th scope="col" class="numeric">Seconds</th><th scope="col" class="numeric">Tokens</th><th scope="col">Message</th>
      </tr></thead><tbody>
__ROWS__
      </tbody></table>
    </div>
    <p class="fine-print">No LLM judge. Every task is checked mechanically. Source: <code>__SRC__</code>. <a href="fork.html#__SUITE__">\u2190 Back to fork results</a></p>
  </main>
</body>
</html>
"""


def _task_message(msg):
    text = str(msg or "").strip()
    if not text:
        return DASH
    short = text if len(text) <= 120 else text[:120] + "\u2026"
    if len(text) <= 120:
        return html.escape(short)
    return (f'<details class="msg"><summary>{html.escape(short)}</summary>'
            f"<pre>{html.escape(text)}</pre></details>")


def render_detail(suite, row, data):
    tasks = [t for t in (data.get("tasks") or data.get("results") or []) if isinstance(t, dict)]
    body = []
    for i, t in enumerate(tasks, 1):
        p = t.get("passed")
        res = "PASS" if p in (True, 1) else ("FAIL" if p in (False, 0) else DASH)
        secs = t.get("elapsed_seconds")
        toks = t.get("agent_total_tokens", t.get("tokens"))
        body.append(
            "<tr>"
            f'<td class="numeric">{i}</td>'
            f"<td>{html.escape(str(t.get('task_id') or t.get('id') or DASH))}</td>"
            f"<td>{res}</td>"
            f'<td class="numeric">{DASH if secs is None else f"{float(secs):.1f}"}</td>'
            f'<td class="numeric">{_fmt_int(toks)}</td>'
            f"<td>{_task_message(t.get('message') or t.get('error'))}</td>"
            "</tr>"
        )
    meta = " \u00b7 ".join([
        f"Profile: {html.escape(row['profile'])}",
        f"Version: {html.escape(row['version'])}",
        f"Result: {html.escape(row['result'])} ({html.escape(row['pct'])})",
        f"Time: {html.escape(row['time'])}",
        f"Steps: {html.escape(row['steps'])}",
        f"Tokens (cost): {html.escape(row['tokens_cost'])}",
    ])
    src = row.get("source_file") or ""
    return (DETAIL_PAGE
            .replace("__TITLE__", html.escape(f"{row['harness']} \u00b7 {row['model']} \u00b7 fork run"))
            .replace("__H1__", html.escape(f"{row['harness']} \u00b7 {row['model']}"))
            .replace("__META__", meta)
            .replace("__N__", str(len(tasks)))
            .replace("__ROWS__", "\n".join(body) or f'<tr><td colspan="6">{DASH}</td></tr>')
            .replace("__SRC__", html.escape(src))
            .replace("__SUITE__", html.escape(suite or "")))


def main(argv):
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
    n = 0
    for detail, suite, row, d in _DETAIL_JOBS:
        (DOCS / detail).write_text(render_detail(suite, row, d), encoding="utf-8")
        n += 1
    counts = ", ".join(f"{s['label']}: {len(s['ours'])}+{len(s['upstream'])}" for s in data["suites"])
    print(f"wrote {OUT_JSON.name} + {OUT_HTML.name} + {n} detail page(s) ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
