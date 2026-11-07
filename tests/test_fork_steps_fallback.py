#!/usr/bin/env python3
"""Tests for the Steps metric resolution (openspec: fix-fork-steps-column).

Covers the source priority used by every fork surface:
  summary.total_steps  ->  top-level steps  ->  sum(tasks[].agent_steps)

Run:  python3 tests/test_fork_steps_fallback.py   (exit 0 = pass)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fork_metrics import steps_from_json  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        FAILS.append(msg)


# 1. aggregate wins
check(steps_from_json({"summary": {"total_steps": 42}, "tasks": [{"agent_steps": 7}]}) == 42,
      "summary.total_steps must take priority")

# 2. top-level fallback
check(steps_from_json({"steps": 9, "tasks": [{"agent_steps": 7}]}) == 9,
      "top-level steps used when summary absent")

# 3. per-task fallback (the OpenClaw case: no aggregate at all)
data = {"summary": {"total": 3}, "tasks": [{"agent_steps": 5}, {"agent_steps": 4}, {"agent_steps": 0}]}
check(steps_from_json(data) == 9, "sum(agent_steps) used when no aggregate")

# 4. genuinely missing -> None (surface renders '—')
check(steps_from_json({"summary": {}, "tasks": [{"passed": True}]}) is None,
      "None when no step data anywhere")
check(steps_from_json({}) is None, "None for empty object")

# 5. weird types are ignored, not crashed on
check(steps_from_json({"tasks": [{"agent_steps": True}, {"agent_steps": None}, {"agent_steps": 3}]}) == 3,
      "bools/None excluded from the per-task sum")

# 6. real artifacts: every committed oc_shotlist file now resolves to a number
for p in sorted((ROOT / "results").glob("oc_shotlist_*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    check(steps_from_json(d) is not None, f"{p.name}: Steps must resolve to a number")

if FAILS:
    print("FAIL:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("ok: steps resolution (priority + fallback + real artifacts)")
