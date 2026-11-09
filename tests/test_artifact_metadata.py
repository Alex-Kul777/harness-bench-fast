"""Artifact metadata header for the fork runners (change: fix-artifact-metadata).

Pins that run_openclaw_bench.py / run_pi_bench.py / run_hermes_bench.py write a
complete, correct top-level metadata header (harness / harness_version / thinking
/ task_set_version / model), that the reasoning level defaults to ``"default"``,
and that ``task_set_version`` is derived from the run's wave (waves 17-19 must not
be recorded as ``"0.16.0"``).
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness_bench.artifact_metadata import (  # noqa: E402
    normalize_thinking,
    resolve_harness_version,
    task_set_version_for_tasks,
)
from harness_bench.versioning import TASK_SET_VERSION  # noqa: E402


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def oc():
    return _load("oc_artifact_metadata", "run_openclaw_bench.py")


@pytest.fixture(scope="module")
def pi():
    return _load("pi_artifact_metadata", "run_pi_bench.py")


@pytest.fixture(scope="module")
def hermes():
    return _load("hermes_artifact_metadata", "run_hermes_bench.py")


# Task ids spanning the wave boundaries (synthetic suffixes keep them cheap).
LIGHT_IDS = ["task_01_create_hello", "task_391_x"]
WAVE17_IDS = ["task_392_manuscript_continuity", "task_411_x"]
WAVE18_IDS = ["task_412_x", "task_431_admin_elevation"]
WAVE19_IDS = ["task_432_clock_contract", "task_471_x"]
WAVES_17_19_IDS = WAVE17_IDS + WAVE18_IDS + WAVE19_IDS


def _rows(task_ids):
    return [
        {"task_id": tid, "passed": True, "elapsed_seconds": 1.0,
         "agent_input_tokens": 10, "agent_output_tokens": 5, "agent_total_tokens": 15}
        for tid in task_ids
    ]


# --------------------------------------------------------------------- helpers

def test_normalize_thinking_defaults():
    assert normalize_thinking(None) == "default"
    assert normalize_thinking("") == "default"
    assert normalize_thinking("   ") == "default"
    assert normalize_thinking("high") == "high"


def test_task_set_version_light_is_0160():
    assert task_set_version_for_tasks(LIGHT_IDS) == "0.16.0"


def test_task_set_version_waves_17_19_not_0160():
    for ids in (WAVE17_IDS, WAVE18_IDS, WAVE19_IDS, WAVES_17_19_IDS):
        version = task_set_version_for_tasks(ids)
        assert version != "0.16.0"
        assert isinstance(version, str) and version


def test_task_set_version_wave_mapping():
    assert task_set_version_for_tasks(WAVE17_IDS) == "0.17.0"
    assert task_set_version_for_tasks(WAVE18_IDS) == "0.18.0"
    assert task_set_version_for_tasks(WAVE19_IDS) == "0.19.1"


def test_task_set_version_empty_falls_back_to_current():
    assert task_set_version_for_tasks([]) == TASK_SET_VERSION


def test_resolve_harness_version_precedence(monkeypatch):
    monkeypatch.setenv("HARNESS_BENCH_HARNESS_VERSION", "env-ver")
    assert resolve_harness_version("explicit-ver") == "explicit-ver"
    assert resolve_harness_version(None) == "env-ver"
    # detect() is used only when flag and env are absent.
    assert resolve_harness_version(None, detect=lambda: "detected-ver") == "env-ver"
    monkeypatch.delenv("HARNESS_BENCH_HARNESS_VERSION", raising=False)
    assert resolve_harness_version(None, detect=lambda: "detected-ver") == "detected-ver"
    assert resolve_harness_version(None, detect=lambda: None) is None


# ------------------------------------------------------------ openclaw runner

def test_openclaw_write_results_metadata(oc, tmp_path):
    out = tmp_path / "oc.json"
    oc._write_results(_rows(WAVES_17_19_IDS), str(out),
                      harness_version="OpenClaw 2026.10.9", model="prov/model-x")
    payload = json.loads(out.read_text())
    assert payload["harness"] == "openclaw"
    assert payload["harness_version"] == "OpenClaw 2026.10.9"
    assert payload["thinking"] == "default"
    assert payload["model"] == "prov/model-x"
    assert payload["task_set_version"] not in (None, "0.16.0")
    assert payload["task_set_version"] == "0.19.1"


def test_openclaw_write_results_thinking_level(oc, tmp_path):
    out = tmp_path / "oc2.json"
    oc._write_results(_rows(WAVE19_IDS), str(out), thinking="high", model="m")
    payload = json.loads(out.read_text())
    assert payload["thinking"] == "high"


def test_openclaw_missing_harness_version_omitted(oc, tmp_path):
    out = tmp_path / "oc3.json"
    oc._write_results(_rows(LIGHT_IDS), str(out), harness_version=None, model="m")
    payload = json.loads(out.read_text())
    assert "harness_version" not in payload
    assert payload["task_set_version"] == "0.16.0"


# ------------------------------------------------------------------ pi runner

def test_pi_write_results_metadata(pi, tmp_path):
    out = tmp_path / "pi.json"
    pi._write_results(_rows(WAVES_17_19_IDS), str(out),
                      model="zai-org/GLM-5.2", task_ids=WAVES_17_19_IDS)
    payload = json.loads(out.read_text())
    assert payload["harness"] == "pi"
    assert payload["thinking"] == "default"
    assert payload["model"] == "zai-org/GLM-5.2"
    assert payload["task_set_version"] not in (None, "0.16.0")
    assert payload["task_set_version"] == "0.19.1"


def test_pi_write_results_thinking_and_version(pi, tmp_path):
    out = tmp_path / "pi2.json"
    pi._write_results(_rows(WAVE18_IDS), str(out), model="m",
                      thinking="medium", harness_version="pi-mono 0.73.1",
                      task_ids=WAVE18_IDS)
    payload = json.loads(out.read_text())
    assert payload["thinking"] == "medium"
    assert payload["harness_version"] == "pi-mono 0.73.1"
    assert payload["task_set_version"] == "0.18.0"


# -------------------------------------------------------------- hermes runner

def test_hermes_write_results_metadata(hermes, tmp_path):
    out = tmp_path / "hermes.json"
    hermes._write_results(_rows(WAVES_17_19_IDS), str(out),
                          model="zai-org/GLM-5.2", task_ids=WAVES_17_19_IDS)
    payload = json.loads(out.read_text())
    assert payload["harness"] == "hermes"
    assert payload["thinking"] == "default"
    assert payload["model"] == "zai-org/GLM-5.2"
    assert payload["task_set_version"] not in (None, "0.16.0")


def test_hermes_thinking_off_records_off(hermes, tmp_path):
    out = tmp_path / "hermes2.json"
    hermes._write_results(_rows(WAVE19_IDS), str(out), model="m",
                          thinking="off", harness_version="hermes 1.2.3",
                          task_ids=WAVE19_IDS)
    payload = json.loads(out.read_text())
    assert payload["thinking"] == "off"
    assert payload["harness_version"] == "hermes 1.2.3"
    assert payload["task_set_version"] == "0.19.1"
