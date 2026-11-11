"""Regression tests for run_hermes_bench.py artifact compliance.

Change: fix-hermes-runner-openspec.

Pins that ``run_hermes_bench._write_results`` writes a COMPLETE metadata header
(top-level ``harness`` / ``thinking`` / ``task_set_version`` / ``model`` and
``harness_version`` when known), records explicit cache/reasoning buckets in the
``summary`` (deriving the cache bucket ONCE from ``total - input - output`` when the
harness exposes none), prices the run at the resolved per-model ₽ rates (never the
hardcoded GLM-5.2 fallback), and that ``--thinking``/``--thinking-off`` map onto the
artifact ``thinking`` field.

Run: python3 -m pytest tests/test_runner_hermes_metadata.py -q
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness_bench.cost_resolver import compute_cost_rub  # noqa: E402

# DeepSeek-V4.1-Flash public ₽/1M rates (catalog cache / config).
DS_RATES = {"input": 64.94, "output": 194.81, "cacheRead": 6.5, "cacheWrite": 0.0}
GLM_FALLBACK = {"input": 239.12, "output": 751.52, "cacheRead": 0.0, "cacheWrite": 0.0}

MODEL = "deepseek-ai/DeepSeek-V4.1-Flash"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hermes():
    return _load("hermes_runner_under_test", "run_hermes_bench.py")


def _rows():
    # Row 1: total (1_000_000) - input (700_000) - output (200_000) = 100_000 cache-read.
    # Row 2: zero tokens (nothing to derive).
    return [
        {
            "task_id": "task_01_create_hello",
            "passed": True,
            "message": "ok",
            "elapsed_seconds": 1.0,
            "agent_input_tokens": 700_000,
            "agent_output_tokens": 200_000,
            "agent_total_tokens": 1_000_000,
            "agent_steps": 3,
        },
        {
            "task_id": "task_412_reflect_x",
            "passed": False,
            "message": "no",
            "elapsed_seconds": 2.0,
            "agent_input_tokens": 0,
            "agent_output_tokens": 0,
            "agent_total_tokens": 0,
            "agent_steps": 1,
        },
    ]


def _write(hermes, tmp_path, monkeypatch, *, rows=None, **kw):
    """Write an artifact with the DS rates stubbed in; return the parsed payload."""
    monkeypatch.setattr(hermes, "_get_model_rates", lambda model_id: dict(DS_RATES))
    path = tmp_path / "hermes_artifact.json"
    hermes._write_results(rows if rows is not None else _rows(), str(path),
                          model=kw.pop("model", MODEL), **kw)
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Metadata header
# ---------------------------------------------------------------------------

def test_header_has_exact_top_level_fields(hermes, tmp_path, monkeypatch):
    payload = _write(hermes, tmp_path, monkeypatch)
    assert payload["harness"] == "hermes"
    assert payload["model"] == MODEL
    assert payload["thinking"] == "default"          # unset -> "default"
    assert isinstance(payload["task_set_version"], str) and payload["task_set_version"]
    # wave-18 ids present -> must NOT be recorded as Light's "0.16.0"
    assert payload["task_set_version"] != "0.16.0"


def test_thinking_level_recorded_when_given(hermes, tmp_path, monkeypatch):
    payload = _write(hermes, tmp_path, monkeypatch, thinking="high")
    assert payload["thinking"] == "high"


def test_harness_version_present_when_known(hermes, tmp_path, monkeypatch):
    payload = _write(hermes, tmp_path, monkeypatch, harness_version="Hermes Agent v0.23.1")
    assert payload["harness_version"] == "Hermes Agent v0.23.1"


def test_harness_version_absent_when_unknown(hermes, tmp_path, monkeypatch):
    payload = _write(hermes, tmp_path, monkeypatch)
    assert "harness_version" not in payload


def test_task_set_version_light_vs_wave(hermes, tmp_path, monkeypatch):
    light = _write(hermes, tmp_path, monkeypatch, rows=[], task_ids=["task_01_create_hello", "task_391_cli_x"])
    assert light["task_set_version"] == "0.16.0"
    wave = _write(hermes, tmp_path, monkeypatch, rows=[], task_ids=["task_412_reflect_x"])
    assert wave["task_set_version"] != "0.16.0"


# ---------------------------------------------------------------------------
# Summary buckets
# ---------------------------------------------------------------------------

def test_summary_has_cache_and_reasoning_buckets(hermes, tmp_path, monkeypatch):
    summary = _write(hermes, tmp_path, monkeypatch)["summary"]
    assert summary["total_cache_read_tokens"] == 100_000
    assert summary["total_cache_write_tokens"] == 0
    assert summary["total_reasoning_tokens"] == 0


def test_cache_bucket_derived_once_from_total(hermes, tmp_path, monkeypatch):
    payload = _write(hermes, tmp_path, monkeypatch)
    row0 = payload["results"][0]
    # Derived value is written back explicitly on the per-task row (OC parity).
    assert row0["agent_cache_read_tokens"] == 100_000
    assert row0["agent_cache_write_tokens"] == 0


def test_explicit_cache_bucket_is_kept(hermes, tmp_path, monkeypatch):
    rows = [dict(_rows()[0], agent_cache_read_tokens=42, agent_cache_write_tokens=7)]
    summary = _write(hermes, tmp_path, monkeypatch, rows=rows)["summary"]
    assert summary["total_cache_read_tokens"] == 42
    assert summary["total_cache_write_tokens"] == 7


# ---------------------------------------------------------------------------
# Cost uses the resolved model rates, not the GLM-5.2 fallback
# ---------------------------------------------------------------------------

def test_cost_uses_model_rates(hermes, tmp_path, monkeypatch):
    summary = _write(hermes, tmp_path, monkeypatch)["summary"]
    expected = round(compute_cost_rub(700_000, 200_000, 100_000, 0, DS_RATES), 2)
    assert expected == 85.07
    assert summary["estimated_cost_rub"] == expected
    glm = round(compute_cost_rub(700_000, 200_000, 100_000, 0, GLM_FALLBACK), 2)
    assert summary["estimated_cost_rub"] != glm


# ---------------------------------------------------------------------------
# CLI wiring: --thinking / --thinking-off map onto the artifact field
# ---------------------------------------------------------------------------

def test_thinking_flag_choices_include_levels(hermes):
    assert "none" in hermes.THINKING_LEVELS
    assert "high" in hermes.THINKING_LEVELS


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
