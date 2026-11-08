"""Suite-selector behaviour for the custom runners (change add-runner-suite-selector).

Each runner exposes ``resolve_task_ids(args)``; this pins the selection order
``--tasks > --suite > ...`` and that ``--suite <name>`` maps to
``harness_bench.tasks.SUITES[name]``.
"""

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness_bench.tasks import SUITES  # noqa: E402

RUNNERS = ("run_pi_bench.py", "run_openclaw_bench.py")


def _load(fname, alias):
    spec = importlib.util.spec_from_file_location(alias, ROOT / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def _args(**kw):
    base = dict(tasks=None, suite=None, pilot=False, shot_list=False,
                failed_only=False, all=False)
    base.update(kw)
    return argparse.Namespace(**base)


def test_suite_selector_matches_registry():
    for i, fname in enumerate(RUNNERS):
        mod = _load(fname, f"runner_suite_{i}")
        for name in ("reflect", "feasibility", "long", "composite-hard"):
            assert mod.resolve_task_ids(_args(suite=name)) == [t.id for t in SUITES[name]]


def test_tasks_override_suite():
    for i, fname in enumerate(RUNNERS):
        mod = _load(fname, f"runner_override_{i}")
        assert mod.resolve_task_ids(_args(tasks=["task_x"], suite="reflect")) == ["task_x"]


def test_no_selection_returns_none():
    for i, fname in enumerate(RUNNERS):
        mod = _load(fname, f"runner_none_{i}")
        assert mod.resolve_task_ids(_args()) is None
