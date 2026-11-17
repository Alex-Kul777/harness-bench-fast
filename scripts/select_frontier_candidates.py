#!/usr/bin/env python3
"""Select "frontier-necessity" candidate tasks from committed result artifacts.

A candidate is a task where the incumbent **DeepSeek-V4.1-Flash** failed at least
once AND at least one *premium/frontier* model passed. These are the tasks where a
top-tier LLM plausibly adds marginal value (hypothesis H2), so they are the
efficient place to spend a limited ₽ budget.

Usage:
    python3 scripts/select_frontier_candidates.py            # write the JSON
    python3 scripts/select_frontier_candidates.py --check    # exit 1 if stale

Output: docs/research/frontier-candidates.json
"""
from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS = REPO_ROOT / "results"
OUT = REPO_ROOT / "docs" / "research" / "frontier-candidates.json"

# Filename token -> canonical model id (last-resort when the envelope omits `model`).
HINTS: tuple[tuple[str, str], ...] = (
    ("gpt55", "openai/gpt-5.5"),
    ("sonnet46", "anthropic/claude-sonnet-4.6"),
    ("opus", "anthropic/claude-opus-4.8"),
    ("gemini", "google/gemini-3.1-pro-preview"),
    ("minimax", "MiniMaxAI/MiniMax-M3"),
    ("glm53", "zai-org/GLM-5.3"),
    ("giga35", "GigaChat3.5"),
    ("gigachat3pro", "GigaChat-3-Pro"),
    ("ds41flash", "deepseek-ai/DeepSeek-V4.1-Flash"),
    ("fable5", "fable-5"),
    ("kimi", "moonshotai/Kimi-K2.6"),
    ("qwen36", "Qwen3.6"),
)
PREMIUM_MARKERS = (
    "gpt-5.5", "sonnet-4.6", "opus-4.8", "gemini-3.1-pro",
    "MiniMax-M3", "Kimi-K2.6", "GLM-5.3", "fable",
)


def _model_of(path: str, env: dict) -> str:
    m = str(env.get("model") or "").strip()
    if m and m not in ("?", "none"):
        return m
    stem = Path(path).name.lower()
    for token, mid in HINTS:
        if token in stem:
            return mid
    return "?"


def _is_deepseek(m: str) -> bool:
    return "deepseek" in m.lower()


def _is_premium(m: str) -> bool:
    return any(marker.lower() in m.lower() for marker in PREMIUM_MARKERS)


def wave_of(task_id: str) -> str:
    m = re.search(r"task_(\d+)", task_id)
    if not m:
        return "?"
    i = int(m.group(1))
    if 392 <= i <= 411:
        return "long-context"
    if 412 <= i <= 431:
        return "tool-reflection"
    if 432 <= i <= 471:
        return "wave19-feasibility"
    if 472 <= i <= 511:
        return "general-hard"
    if 512 <= i <= 531:
        return "composite-hard"
    return f"legacy/{i}"


def collect() -> dict:
    ds: dict[str, list[int]] = collections.defaultdict(lambda: [0, 0])
    prem: dict[str, set[str]] = collections.defaultdict(set)
    for path in glob.glob(str(RESULTS / "*.json")):
        try:
            env = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            continue
        res = env.get("results") or env.get("tasks")
        if not res:
            continue
        model = _model_of(path, env)
        for row in res:
            tid = row.get("task_id") or row.get("id")
            if not tid:
                continue
            passed = bool(row.get("passed"))
            if _is_deepseek(model):
                ds[tid][0] += 1
                ds[tid][1] += int(passed)
            elif _is_premium(model) and passed:
                prem[tid].add(model)

    candidates = []
    for tid, (n, k) in ds.items():
        if n >= 1 and k < n and prem.get(tid):
            candidates.append({
                "task_id": tid,
                "wave": wave_of(tid),
                "deepseek_failed": n - k,
                "deepseek_runs": n,
                "premium_passed": sorted(prem[tid]),
                "premium_passed_n": len(prem[tid]),
            })
    # Rank: most robust DeepSeek failure first, then broadest premium support.
    candidates.sort(key=lambda c: (c["deepseek_runs"] - c["deepseek_failed"],
                                   -c["premium_passed_n"], c["task_id"]))
    waves = collections.Counter(c["wave"] for c in candidates)
    return {
        "generated": "2026-11-17",
        "source": "results/*.json (committed artifacts)",
        "note": "DeepSeek-V4.1-Flash failed >=1x AND >=1 premium model passed.",
        "candidate_count": len(candidates),
        "by_wave": dict(waves),
        "candidates": candidates,
    }


def main(argv: list[str]) -> int:
    data = collect()
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if "--check" in argv:
        if current != out:
            print("STALE: docs/research/frontier-candidates.json", file=sys.stderr)
            return 1
        print("frontier-candidates.json: up to date")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if current != out:
        OUT.write_text(out, encoding="utf-8")
        print(f"frontier-candidates.json: written ({data['candidate_count']} candidates)")
    else:
        print("frontier-candidates.json: up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
