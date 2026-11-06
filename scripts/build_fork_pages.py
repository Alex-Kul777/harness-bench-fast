#!/usr/bin/env python3
"""Generate docs/fork-medium90-results.json for the fork results pages.

Scans run JSON in ``<repo>/results`` (checkout wins) then ``<repo>/../results``
(de-duplicated by file name), keeps only runs whose file-name stem belongs to one
of the Medium umbrella waves, aggregates them per (harness, model, profile) and
writes the *frozen* schema from
``openspec/changes/add-fork-results-pages/design.md``.

Waves (umbrella suite "Medium (392-471)"):
    long        392-411  20 tasks   (stem token "long")
    reflect     412-431  20 tasks   (stem token "reflect")
    feasibility 432-471  40 tasks   (stem token "feasibility" or "wave19")

Usage:
    python3 scripts/build_fork_pages.py                 # write docs/fork-medium90-results.json
    python3 scripts/build_fork_pages.py --check         # exit 1 if the file is stale
    python3 scripts/build_fork_pages.py --json          # print the JSON to stdout
    python3 scripts/build_fork_pages.py --out PATH      # write/compare against PATH
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "docs" / "fork-medium90-results.json"

# Checkout's own results win on a name clash; the shared store lives one level up.
RESULT_DIRS = [REPO_ROOT / "results", REPO_ROOT.parent / "results"]

GENERATED_BY = "scripts/build_fork_pages.py"
TASK_SET_VERSION = "v0.21.3"
MEDIUM_TASKS = 80
PROVENANCE = (
    "Fork run artifacts scanned from results/ (checkout first) + ../results/, "
    "de-duplicated by file name; k=1 (no repeats per config); no infra failures "
    "recorded; partial = summed total < expected tasks for the wave."
)

# key -> (label, task_range, expected tasks)
WAVES = {
    "long": ("Long context", "392\u2013411", 20),
    "reflect": ("Tool reflection", "412\u2013431", 20),
    "feasibility": ("Feasibility", "432\u2013471", 40),
}
WAVE_ORDER = ["long", "reflect", "feasibility"]

REQUIRED_SUMMARY_FIELDS = (
    "passed",
    "total",
    "pass_rate",
    "total_seconds",
    "total_steps",
    "total_tokens",
    "estimated_cost_rub",
)

# longest prefixes first
HARNESS_PREFIXES = (
    ("opencode_", "opencode"),
    ("openclaw_", "OpenClaw"),
    ("opencode", "opencode"),
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

PROFILE_RULES = (
    ("thinking_off", "thinking: off"),
    ("mcpoff", "MCP off"),
)

# Non-publishable artifacts (smoke/sample/diagnostic/rerun) never reach the page.
EXCLUDE_KEYWORDS = ("smoke", "sample", "diag", "part2", "rerun")

# Known fork wave artifacts whose file name lacks the harness/model token.
# (Explicit, documented: avoids a bogus "unknown" row for real runs.)
RUN_META_OVERRIDES = {
    "pi_pilot_long3": {"model": "DeepSeek-V4.1-Flash"},
    "wave19_full_ds41flash": {"harness": "Pi"},
}

WILSON_Z = 1.96


def _override(stem: str, field: str) -> str | None:
    lower = stem.lower()
    for prefix, meta in RUN_META_OVERRIDES.items():
        if prefix in lower and field in meta:
            return meta[field]
    return None


def classify_wave(stem: str) -> str | None:
    lower = stem.lower()
    if "long" in lower:
        return "long"
    if "reflect" in lower:
        return "reflect"
    if "feasibility" in lower or "wave19" in lower:
        return "feasibility"
    return None


def classify_harness(stem: str) -> str | None:
    lower = stem.lower()
    for prefix, harness in HARNESS_PREFIXES:
        if lower.startswith(prefix):
            return harness
    return None


def classify_model(stem: str) -> str | None:
    lower = stem.lower()
    for token, model in MODEL_TOKENS:
        if token in lower:
            return model
    return None


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


def wilson_interval(passed: int, total: int, z: float = WILSON_Z) -> list[float]:
    """95% Wilson score interval for passed/total, rounded to 3 decimals."""
    if total <= 0:
        return [0.0, 0.0]
    n = float(total)
    p = passed / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = (z / math.sqrt(n)) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / denom
    lo = max(0.0, center - half)
    hi = min(1.0, center + half)
    return [round(lo, 3), round(hi, 3)]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def row_id(harness, model, profile) -> str:
    parts = [_slug(p) for p in (harness, model, profile) if p]
    parts = [p for p in parts if p]
    return "-".join(parts) if parts else "unknown"


def build_model() -> dict:
    groups: dict[tuple, dict] = {}

    for name, path in collect_paths().items():
        stem = path.stem
        lower = stem.lower()
        wave = classify_wave(stem)
        if wave is None:
            continue
        if any(keyword in lower for keyword in EXCLUDE_KEYWORDS):
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
        if any(field not in summary for field in REQUIRED_SUMMARY_FIELDS):
            print(f"[skip] {name}: summary missing required fields", file=sys.stderr)
            continue

        harness = classify_harness(stem) or _override(stem, "harness")
        model = classify_model(stem) or _override(stem, "model")
        if harness is None or model is None:
            print(f"[skip] {name}: unresolved harness/model", file=sys.stderr)
            continue

        key = (harness, model, classify_profile(stem))
        group = groups.setdefault(
            key,
            {
                "suites": {w: {"passed": 0, "total": 0} for w in WAVE_ORDER},
                "usage": {"seconds": 0.0, "steps": 0, "tokens": 0, "cost_rub": 0.0},
                "sources": [],
            },
        )
        suit = group["suites"][wave]
        suit["passed"] += int(summary.get("passed") or 0)
        suit["total"] += int(summary.get("total") or 0)

        usage = group["usage"]
        usage["seconds"] += float(summary.get("total_seconds") or 0.0)
        usage["steps"] += int(summary.get("total_steps") or 0)
        usage["tokens"] += int(summary.get("total_tokens") or 0)
        usage["cost_rub"] += float(summary.get("estimated_cost_rub") or 0.0)
        group["sources"].append(name)

    rows: list[dict] = []
    for (harness, model, profile), group in groups.items():
        suites: dict[str, object] = {}
        wilson: dict[str, list[float]] = {}
        for wave in WAVE_ORDER:
            agg = group["suites"][wave]
            if not _wave_present(group, wave):
                # No run contributed to this wave => unmeasured (not a failure).
                suites[wave] = None
                continue
            expected = WAVES[wave][2]
            measurement = "partial" if agg["total"] < expected else "complete"
            suites[wave] = {
                "passed": agg["passed"],
                "total": agg["total"],
                "measurement": measurement,
            }
            wilson[wave] = wilson_interval(agg["passed"], agg["total"])

        rows.append(
            {
                "id": row_id(harness, model, profile),
                "harness": harness,
                "model": model,
                "profile": profile,
                "runs": len(group["sources"]),
                "suites": suites,
                "usage": {
                    "seconds": round(group["usage"]["seconds"], 1),
                    "steps": group["usage"]["steps"],
                    "tokens": group["usage"]["tokens"],
                    "cost_rub": round(group["usage"]["cost_rub"], 1),
                },
                "wilson": wilson,
                "sources": sorted(group["sources"]),
            }
        )

    rows.sort(
        key=lambda r: (
            r["harness"] is None,
            r["harness"] or "",
            r["model"] or "",
            r["profile"] or "",
        )
    )

    return {
        "generated_by": GENERATED_BY,
        "task_set_version": TASK_SET_VERSION,
        "medium_tasks": MEDIUM_TASKS,
        "provenance": PROVENANCE,
        "waves": [
            {
                "key": key,
                "label": WAVES[key][0],
                "task_range": WAVES[key][1],
                "tasks": WAVES[key][2],
            }
            for key in WAVE_ORDER
        ],
        "rows": rows,
    }


def _wave_present(group: dict, wave: str) -> bool:
    agg = group["suites"][wave]
    return agg["total"] > 0 or agg["passed"] > 0


def render(model: dict) -> str:
    return json.dumps(model, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    out_path = DEFAULT_OUT
    if "--out" in argv:
        idx = argv.index("--out")
        try:
            out_path = Path(argv[idx + 1])
        except IndexError:
            print("error: --out requires a PATH", file=sys.stderr)
            return 2

    emit_json = "--json" in argv
    check = "--check" in argv

    model = build_model()
    text = render(model)

    if emit_json:
        sys.stdout.write(text)
        return 0

    if check:
        try:
            current = out_path.read_text(encoding="utf-8")
        except OSError:
            current = None
        if current != text:
            print(f"{out_path.name}: STALE \u2014 run: python3 scripts/build_fork_pages.py")
            return 1
        print(f"{out_path.name}: up to date ({len(model['rows'])} rows)")
        return 0

    try:
        current = out_path.read_text(encoding="utf-8")
    except OSError:
        current = None
    if current == text:
        print(f"{out_path.name}: already up to date ({len(model['rows'])} rows)")
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"{out_path.name}: written ({len(model['rows'])} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
