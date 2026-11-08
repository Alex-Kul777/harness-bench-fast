"""Artifact metadata for the OpenClaw runner (change: record harness_version + thinking).

Pins that ``run_openclaw_bench.py`` writes ``harness_version`` and the effective
``thinking`` level into the results JSON, and resolves the version with
explicit > env > autodetect precedence.
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness-bench-fast"))


def _load():
    spec = importlib.util.spec_from_file_location(
        "oc_runner_version", ROOT / "run_openclaw_bench.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["oc_runner_version"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_resolve_harness_version_precedence(monkeypatch):
    mod = _load()
    monkeypatch.setenv("HARNESS_BENCH_HARNESS_VERSION", "env-ver")
    assert mod.resolve_harness_version("explicit-ver") == "explicit-ver"
    assert mod.resolve_harness_version(None) == "env-ver"
    monkeypatch.delenv("HARNESS_BENCH_HARNESS_VERSION", raising=False)
    # no explicit + no env -> autodetect; must not raise (str or None)
    got = mod.resolve_harness_version(None)
    assert got is None or isinstance(got, str)


def test_write_results_records_metadata(tmp_path):
    mod = _load()
    out = tmp_path / "res.json"
    rows = [{
        "task_id": "t1", "passed": True, "elapsed_seconds": 1.0,
        "agent_input_tokens": 10, "agent_output_tokens": 5,
        "agent_total_tokens": 15, "thinking": "high",
    }]
    mod._write_results(
        rows, str(out),
        harness_version="OpenClaw 2026.10.9 (8b18b55)",
        thinking="high",
        command="python run_openclaw_bench.py --shot-list --thinking high",
    )
    payload = json.loads(out.read_text())
    assert payload["harness"] == "openclaw"
    assert payload["harness_version"] == "OpenClaw 2026.10.9 (8b18b55)"
    assert payload["thinking"] == "high"
    assert payload["command"].endswith("--thinking high")
    assert payload["tasks"][0]["thinking"] == "high"
