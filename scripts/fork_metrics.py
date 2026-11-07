"""Shared fork reporting metrics.

Single source of truth for cross-surface values so the HTML pages and the
markdown auto-block agree. See openspec change ``fix-fork-steps-column``.
"""
from __future__ import annotations

from typing import Any


def _per_task_steps(tasks: Any) -> int | None:
    if not isinstance(tasks, list):
        return None
    total = 0
    seen = False
    for task in tasks:
        if not isinstance(task, dict):
            continue
        value = task.get("agent_steps")
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            total += value
            seen = True
    return int(total) if seen else None


def steps_from_json(data: Any) -> int | None:
    """Resolve the 'Steps' value for a run JSON.

    Priority: ``summary.total_steps`` -> top-level ``steps`` -> sum of
    per-task ``agent_steps`` (``toolSummary.calls`` for the OpenClaw runner).
    Returns ``None`` only when no source carries step data, so surfaces can
    still render ``—`` for genuinely missing values.
    """
    if not isinstance(data, dict):
        return None
    summary = data.get("summary")
    if isinstance(summary, dict):
        value = summary.get("total_steps")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value)
    value = data.get("steps")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value)
    return _per_task_steps(data.get("tasks") or data.get("results"))
