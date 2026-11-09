"""Shared top-level artifact metadata for the fork benchmark runners.

Each run artifact carries a complete, correct metadata header so a result can be
interpreted and resumed without ambiguity. The frozen contract (field names must
not be renamed) is:

    harness           - harness name ("openclaw" / "pi" / "hermes")
    harness_version   - harness (CLI) version; omitted only if truly unknown
    thinking          - effective reasoning level, or "default" when unset
    task_set_version  - task-set version CORRECT for the run's wave
    model             - exact model id/version

``run_openclaw_bench.py``, ``run_pi_bench.py`` and ``run_hermes_bench.py`` build
their headers through :func:`artifact_metadata`.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable

from harness_bench.versioning import TASK_SET_REVISIONS, TASK_SET_VERSION, task_number

DEFAULT_THINKING = "default"


def normalize_thinking(value: str | None) -> str:
    """Return the effective reasoning level, or ``"default"`` when unset."""
    if value is None:
        return DEFAULT_THINKING
    text = str(value).strip()
    return text or DEFAULT_THINKING


def task_set_version_for_tasks(task_ids: Iterable[str]) -> str:
    """Return the task-set version that defines the run's wave.

    Picks the *tightest* revision-history entry whose ``total_tasks`` covers the
    highest task number in *task_ids*; among revisions sharing that ``total_tasks``
    the latest wins (later protocol revisions add no tasks). Unknown/empty input
    falls back to the current :data:`TASK_SET_VERSION`.

    This keeps Light (1-391) at ``"0.16.0"`` while waves 17-19 (392-471) record
    their own revisions instead of a hardcoded value.
    """
    numbers: list[int] = []
    for task_id in task_ids:
        number = task_number(str(task_id))
        if number is not None:
            numbers.append(number)
    if not numbers:
        return TASK_SET_VERSION
    top = max(numbers)
    covering = [rev.total_tasks for rev in TASK_SET_REVISIONS if rev.total_tasks >= top]
    if not covering:
        return TASK_SET_VERSION
    tightest = min(covering)
    for revision in reversed(TASK_SET_REVISIONS):
        if revision.total_tasks == tightest:
            return revision.version
    return TASK_SET_VERSION


def resolve_harness_version(
    explicit: str | None = None,
    *,
    detect: Callable[[], str | None] | None = None,
) -> str | None:
    """Resolve a harness version: explicit flag > env > best-effort ``detect()``.

    ``detect`` failures are swallowed (a version that cannot be determined is
    left absent rather than invented).
    """
    if explicit:
        return explicit
    env = os.environ.get("HARNESS_BENCH_HARNESS_VERSION")
    if env:
        return env
    if detect is not None:
        try:
            value = detect()
        except Exception:  # noqa: BLE001 - detection is best-effort
            return None
        return value or None
    return None


def artifact_metadata(
    *,
    harness: str,
    task_ids: Iterable[str],
    thinking: str | None = None,
    harness_version: str | None = None,
    model: str | None = None,
) -> dict:
    """Build the ordered top-level metadata header for a run artifact.

    Always includes ``task_set_version``, ``harness``, ``thinking`` and (when
    ``model`` is provided) ``model``. ``harness_version`` is included only when
    known.
    """
    meta: dict[str, str] = {
        "task_set_version": task_set_version_for_tasks(task_ids),
        "harness": harness,
    }
    if harness_version:
        meta["harness_version"] = harness_version
    meta["thinking"] = normalize_thinking(thinking)
    if model is not None:
        meta["model"] = model
    return meta
