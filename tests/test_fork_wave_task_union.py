"""Regression: fork Medium wave totals de-duplicate tasks by UNION of numbers.

Covers the OpenClaw x DeepSeek-V4.1-Flash (thinking: off) bug: a superseded
2-task partial long run plus its 6-task catch-up summed to 8 instead of the 6
distinct tasks actually covered. ``build_fork_pages.build_model`` must union
task numbers per (config, wave) instead of summing per-file summary totals.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_fork_pages as bfp  # noqa: E402


def _summary(passed: int, total: int) -> dict:
    return {
        "passed": passed,
        "total": total,
        "pass_rate": (passed / total) if total else 0.0,
        "total_seconds": 1.0,
        "total_steps": 1,
        "total_tokens": 1,
        "estimated_cost_rub": 1.0,
    }


def _artifact(task_key: str, entries: list[dict]) -> dict:
    """One run artifact; per-task entries live under *task_key* (tasks|results)."""
    return {
        "summary": _summary(sum(1 for e in entries if e["passed"]), len(entries)),
        task_key: entries,
    }


# A superseded partial long run (2 tasks) ...
PARTIAL = [
    {"task_id": "task_392_manuscript_continuity", "passed": False},
    {"task_id": "task_393_intranet_multihop", "passed": False},
]
# ... and its catch-up (6 tasks, overlapping 392/393).
CATCHUP = [
    {"task_id": "task_392_manuscript_continuity", "passed": False},
    {"task_id": "task_393_intranet_multihop", "passed": False},
    {"task_id": "task_394_review_annotation", "passed": True},
    {"task_id": "task_395_homework_grading", "passed": True},
    {"task_id": "task_398_card_game_engine", "passed": False},
    {"task_id": "task_403_binary_format_reverse", "passed": False},
]


def _write(tmp_path: Path, name: str, artifact: dict) -> None:
    (tmp_path / name).write_text(json.dumps(artifact), encoding="utf-8")


def _off_row(model: dict) -> dict:
    rid = bfp.row_id("OpenClaw", "DeepSeek-V4.1-Flash", "thinking: off")
    matches = [r for r in model["rows"] if r["id"] == rid]
    assert matches, "off config row missing"
    return matches[0]


@pytest.mark.parametrize("task_key", ["tasks", "results"])
def test_overlapping_long_artifacts_do_not_inflate_wave(tmp_path, task_key):
    """2 + 6 overlapping -> 6 distinct, passed = sum over the union."""
    _write(tmp_path, "oc_medium_long_ds41flash_off_20261108.json", _artifact(task_key, PARTIAL))
    _write(tmp_path, "oc_medium_long_ds41flash_off_20261109.json", _artifact(task_key, CATCHUP))

    row = _off_row(bfp.build_model(result_dirs=[tmp_path]))
    suite = row["suites"]["long"]
    assert suite["total"] == 6, suite          # NOT 8 (the old summed bug)
    assert suite["passed"] == 2, suite
    assert suite["measurement"] == "partial"
    # Untouched waves stay unmeasured (no zeros invented).
    assert row["suites"]["reflect"] is None
    assert row["suites"]["feasibility"] is None


def test_later_artifact_supersedes_earlier_for_same_number(tmp_path):
    """Ascending file-name order: the later artifact wins per task number."""
    _write(
        tmp_path,
        "oc_medium_long_ds41flash_off_20261108.json",
        _artifact("tasks", [{"task_id": "task_392_x", "passed": True}]),
    )
    _write(
        tmp_path,
        "oc_medium_long_ds41flash_off_20261109.json",
        _artifact("tasks", [{"task_id": "task_392_x", "passed": False}]),
    )
    suite = _off_row(bfp.build_model(result_dirs=[tmp_path]))["suites"]["long"]
    assert suite["total"] == 1, suite
    assert suite["passed"] == 0, suite  # later False supersedes earlier True


def test_number_field_is_preferred_over_task_id_regex(tmp_path):
    """`number` wins; the task_id regex is only a fallback."""
    _write(
        tmp_path,
        "oc_medium_long_ds41flash_off_20261108.json",
        _artifact("tasks", [{"number": 392, "task_id": "task_999_decoy", "passed": True}]),
    )
    suite = _off_row(bfp.build_model(result_dirs=[tmp_path]))["suites"]["long"]
    assert suite["total"] == 1, suite
    assert suite["passed"] == 1, suite


def test_fallback_sums_totals_without_parseable_numbers(tmp_path):
    """No parseable task numbers anywhere -> legacy summation for that wave."""
    _write(tmp_path, "oc_medium_reflect_ds41flash_off_20261108.json", {"summary": _summary(3, 20), "tasks": []})
    _write(tmp_path, "oc_medium_reflect_ds41flash_off_20261109.json", {"summary": _summary(4, 20)})
    suite = _off_row(bfp.build_model(result_dirs=[tmp_path]))["suites"]["reflect"]
    assert suite["total"] == 40, suite
    assert suite["passed"] == 7, suite
