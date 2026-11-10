#!/usr/bin/env python3
"""Regression test for the Pi-runner status-file model bug.

Defect (2026-11-10): ``run_pi_bench.py::_write_status`` referenced ``model`` in
``_get_model_rates(model or DEFAULT_MODEL)`` but never received it as a parameter
-> ``NameError: name 'model' is not defined`` right after a run finished. The two
call sites in ``run_batch`` omitted it too.

RED  (pre-fix): the first ``_write_status(...)`` call without an explicit model
               raises ``NameError``.
GREEN (post-fix): it writes a status JSON, and an explicit non-default model is
               used for the cost calculation.

Run: python3 -m pytest tests/test_runner_pi_status_model.py -q
 or: python3 tests/test_runner_pi_status_model.py
"""
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_pi_bench as rpb  # noqa: E402


def _results():
    return [
        {"task_id": "task_a", "passed": True,
         "agent_input_tokens": 1000, "agent_output_tokens": 500},
        {"task_id": "task_b", "passed": False,
         "agent_input_tokens": 200, "agent_output_tokens": 100},
    ]


class TestWriteStatusModel(unittest.TestCase):
    def test_write_status_without_model_does_not_raise_nameerror(self):
        """RED pre-fix: NameError; GREEN post-fix: writes status JSON."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "status.json"
            # No `model` argument -> pre-fix this raises NameError.
            rpb._write_status(path, 2, 2, _results(), time.monotonic() - 1.0)
            data = json.loads(path.read_text())
        self.assertEqual(data["completed"], 2)
        self.assertEqual(data["passed"], 1)
        self.assertEqual(data["failed"], 1)
        self.assertIn("estimated_cost_rub", data)
        # Default model rates drive the cost when no model is supplied.
        self.assertAlmostEqual(
            data["estimated_cost_rub"],
            round(rpb.compute_cost_rub(1200, 600, 0, 0,
                                       rpb._get_model_rates(rpb.DEFAULT_MODEL)), 2),
            places=2,
        )

    def test_write_status_uses_explicit_non_default_model(self):
        """An explicit non-default model is used for the cost calculation."""
        model = "deepseek-ai/DeepSeek-V4.1-Flash"
        rates = {"input": 11.0, "output": 22.0, "cacheRead": 0.0, "cacheWrite": 0.0}
        seen = {}

        def fake_rates(model_id):
            seen["model"] = model_id
            return rates

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "status.json"
            with mock.patch.object(rpb, "_get_model_rates", side_effect=fake_rates):
                rpb._write_status(path, 2, 2, _results(), time.monotonic() - 1.0,
                                  model=model)
            data = json.loads(path.read_text())

        self.assertEqual(seen.get("model"), model)
        self.assertAlmostEqual(
            data["estimated_cost_rub"],
            round(rpb.compute_cost_rub(1200, 600, 0, 0, rates), 2),
            places=2,
        )


if __name__ == "__main__":
    unittest.main()
