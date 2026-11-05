#!/usr/bin/env python3
"""Rebuild the auto-synced fork results block in docs/fork-results.md.

Scans ``results/*.json`` (the repo root is resolved from this script's own
location: ``<repo>/scripts/..``), keeps only the "main" runs, and regenerates
the markdown summary table between the ``FORK:RESULTS`` markers.

Usage:
    python3 scripts/build_fork_results.py           # rewrite the block
    python3 scripts/build_fork_results.py --check   # exit 1 if the block is stale
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "fork-results.md"

BEGIN_MARKER = "<!-- FORK:RESULTS:BEGIN -->"
END_MARKER = "<!-- FORK:RESULTS:END -->"

# The fork keeps its published runs in ``<repo>/results``; the shared project
# run store lives one level up and uses the same file names. Aggregate both,
# de-duplicated by file name (the checkout's own copy wins on a tie).
RESULT_DIRS = [REPO_ROOT / "results", REPO_ROOT.parent / "results"]

HARNESS_PREFIXES = (
    ("opencode_", "opencode"),
    ("hermes_", "Hermes"),
    ("pi_", "Pi"),
    ("oc_", "OpenClaw"),
)

MODEL_TOKENS = (
    ("ds41flash", "DeepSeek-V4.1-Flash"),
    ("glm53", "GLM-5.3"),
    ("glm52", "GLM-5.2"),
    ("qwen36", "Qwen3.6-35B-A3B"),
    ("oss120b", "GPT-OSS-120B"),
)
THINKING_OFF_SUFFIX = "thinking_off"
THINKING_OFF_MODEL = "GLM-5.2 (thinking: off)"

# suite key -> (display name, sort order)
SUITES = {
    "shotlist": ("Shot List (52)", 0),
    "full_391": ("Light (391)", 1),
    "wave19_full": ("Wave 19 (40)", 2),
}
SUITE_ORDER = {name: order for name, order in SUITES.values()}

INCLUDE_RE = re.compile(r"(_shotlist_|_full_391|wave19_full_)")
EXCLUDE_KEYWORDS = ("part2", "rerun", "pilot", "smoke", "diag", "sample")

DASH = "\u2014"
COST_UNIT = "\u20bd"  # ₽

# --- lint: canonical columns in the fork's result tables -------------------
LINT_FILES = [REPO_ROOT / "FORK.md", DOC_PATH]
REQUIRED_COLUMNS = ["Harness", "Profile", "Model", "Result", "%", "Time", "Steps", "Tokens"]


def _is_results_header(cells: list[str]) -> bool:
    low = [c.lower() for c in cells]
    return "model" in low and "result" in low


def _missing_columns(cells: list[str]) -> list[str]:
    missing: list[str] = []
    for req in REQUIRED_COLUMNS:
        if req == "Tokens":
            ok = any(c.lower().startswith("tokens") for c in cells)
        else:
            ok = any(c.lower() == req.lower() for c in cells)
        if not ok:
            missing.append(req)
    return missing


def lint_docs() -> list[tuple[str, int, list[str]]]:
    problems: list[tuple[str, int, list[str]]] = []
    for path in LINT_FILES:
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if _is_results_header(cells):
                missing = _missing_columns(cells)
                if missing:
                    problems.append((path.name, lineno, missing))
    return problems


def classify_suite(stem: str) -> str | None:
    if "wave19_full_" in stem:
        return "Wave 19 (40)"
    if "_full_391" in stem:
        return "Light (391)"
    if "_shotlist_" in stem:
        return "Shot List (52)"
    return None


def classify_harness(stem: str) -> str | None:
    for prefix, harness in HARNESS_PREFIXES:
        if stem.startswith(prefix):
            return harness
    return None


def classify_model(stem: str) -> str | None:
    if THINKING_OFF_SUFFIX in stem:
        return THINKING_OFF_MODEL
    for token, model in MODEL_TOKENS:
        if token in stem:
            return model
    return None


PROFILE_RULES = (
    ("thinking_off", "thinking: off"),
    ("mcpoff", "MCP off"),
)


def classify_profile(stem: str) -> str | None:
    lower = stem.lower()
    for token, label in PROFILE_RULES:
        if token in lower:
            return label
    return None


def collect_paths() -> dict[str, Path]:
    """Return {file name: path} across the result dirs (first dir wins)."""
    seen: dict[str, Path] = {}
    for directory in RESULT_DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            seen.setdefault(path.name, path)
    return seen


def fmt_result(passed, total) -> str:
    if passed is None or total is None:
        return DASH
    return f"{int(passed)}/{int(total)}"


def fmt_pct(pass_rate) -> str:
    if pass_rate is None:
        return DASH
    pct = pass_rate * 100 if pass_rate <= 1 else float(pass_rate)
    return f"{pct:.1f}%"


def fmt_time(seconds) -> str:
    if seconds is None:
        return DASH
    return f"{float(seconds) / 60:.1f}m"


def fmt_int(value) -> str:
    if value is None:
        return DASH
    return f"{int(value):,}".replace(",", " ")


def fmt_cost(value) -> str:
    if value is None:
        return DASH
    return f"{float(value):,.0f}".replace(",", " ") + COST_UNIT


def build_rows() -> list[dict]:
    rows: list[dict] = []
    for name, path in collect_paths().items():
        stem = path.stem
        lower = stem.lower()
        if not INCLUDE_RE.search(stem):
            continue
        if any(keyword in lower for keyword in EXCLUDE_KEYWORDS):
            continue
        suite = classify_suite(stem)
        if suite is None:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[skip] {name}: unreadable ({exc})", file=sys.stderr)
            continue
        summary = data.get("summary")
        if not isinstance(summary, dict):
            print(f"[skip] {name}: no summary object", file=sys.stderr)
            continue
        rows.append(
            {
                "harness": classify_harness(stem),
                "suite": suite,
                "profile": classify_profile(stem),
                "model": classify_model(stem),
                "result": fmt_result(summary.get("passed"), summary.get("total")),
                "pct": fmt_pct(summary.get("pass_rate")),
                "time": fmt_time(summary.get("total_seconds")),
                "steps": fmt_int(summary.get("total_steps")),
                "tokens": fmt_int(summary.get("total_tokens")),
                "cost": fmt_cost(summary.get("estimated_cost_rub")),
                "_passed": summary.get("passed") or 0,
            }
        )
    rows.sort(
        key=lambda r: (
            (0, r["harness"]) if r["harness"] else (1, ""),
            SUITE_ORDER[r["suite"]],
            r["model"] or "",
            -(r["_passed"] or 0),
        )
    )
    return rows


def render_block(rows: list[dict]) -> str:
    lines = [
        f"\u0410\u0432\u0442\u043e\u0441\u0438\u043d\u043a: {len(rows)} \u043f\u0440\u043e\u0433\u043e\u043d\u043e\u0432",
        "",
        "| Harness | Suite | Profile | Model | Result | % | Time | Steps | Tokens (cost) |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in rows:
        cells = [
            r["harness"] or DASH,
            r["suite"],
            r["profile"] or DASH,
            r["model"] or DASH,
            r["result"],
            r["pct"],
            r["time"],
            r["steps"],
            f"{r['tokens']} ({r['cost']})",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def splice(doc: str, block: str) -> str:
    begin = doc.find(BEGIN_MARKER)
    end = doc.find(END_MARKER)
    if begin == -1 or end == -1 or end < begin:
        raise SystemExit(f"error: markers not found in {DOC_PATH}")
    head = doc[: begin + len(BEGIN_MARKER)]
    tail = doc[end:]
    return f"{head}\n{block}\n{tail}"


def main(argv: list[str]) -> int:
    if "--lint" in argv:
        problems = lint_docs()
        if problems:
            for name, lineno, missing in problems:
                print(
                    f"{name}:{lineno}: result table missing columns: {', '.join(missing)}",
                    file=sys.stderr,
                )
            return 1
        print("lint: all result tables have canonical columns")
        return 0
    check = "--check" in argv
    rows = build_rows()
    block = render_block(rows)
    try:
        doc = DOC_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {DOC_PATH}: {exc}", file=sys.stderr)
        return 2

    updated = splice(doc, block)
    if check:
        if updated == doc:
            print(f"{DOC_PATH.name}: up to date ({len(rows)} runs)")
            return 0
        print(f"{DOC_PATH.name}: STALE — run: python3 scripts/build_fork_results.py")
        return 1

    if updated == doc:
        print(f"{DOC_PATH.name}: already up to date ({len(rows)} runs)")
        return 0
    DOC_PATH.write_text(updated, encoding="utf-8")
    print(f"{DOC_PATH.name}: updated ({len(rows)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
