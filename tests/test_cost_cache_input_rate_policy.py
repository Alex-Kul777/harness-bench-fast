"""Owner policy H2 (change ``price-cache-read-at-input-rate``).

A model with **no published cache tariff** (``cacheRead`` / ``cacheWrite``
absent or 0) prices its cache-read / cache-write tokens at the model's INPUT
rate; a published cache rate (DeepSeek-V4.1-Flash = 6.5) is kept.  The runner
and the RUB backfill also record the cache bucket EXPLICITLY
(``total_cache_read_tokens``) so it is never re-derived at read time.

These tests are red before the change and green after it.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from harness_bench.cost_resolver import compute_cost_rub, resolve_model_rates  # noqa: E402

# No cache tariff (catalog ``cache_read`` = 0.0) -> priced at the INPUT rate.
_MINIMAX = {"input": 240.218, "output": 1008.8546, "cacheRead": 0.0, "cacheWrite": 0.0}
_GIGACHAT3PRO = {"input": 73.03, "output": 176.39, "cacheRead": 0.0, "cacheWrite": 0.0}
# Published cache tariff -> kept as-is.
_DS41FLASH = {"input": 64.94, "output": 194.81, "cacheRead": 6.5, "cacheWrite": 0.0}

_CATALOG = {
    "fetched_at": "2026-11-09T00:00:00+00:00",
    "models": {
        "MiniMaxAI/MiniMax-M3": {
            "input": 240.218, "output": 1008.8546, "cache_read": 0.0, "is_billable": True,
        },
        "deepseek-ai/DeepSeek-V4.1-Flash": {
            "input": 64.94, "output": 194.81, "cache_read": 6.5, "is_billable": True,
        },
    },
}


@pytest.fixture()
def cache_path(tmp_path, monkeypatch):
    cache = tmp_path / "cloudru-prices.json"
    cache.write_text(json.dumps(_CATALOG), encoding="utf-8")
    monkeypatch.setenv("CLOUDRU_PRICES_CACHE", str(cache))
    return str(cache)


# ---------------------------------------------------------------------------
# Pricing policy
# ---------------------------------------------------------------------------

def test_none_cache_model_prices_cache_read_at_input_rate():
    inp, out, cache = 1_000_000, 0, 2_000_000
    cost = compute_cost_rub(inp, out, cache, 0, _MINIMAX)
    assert cost == pytest.approx((inp + cache) / 1e6 * 240.218, rel=1e-9)
    assert cost > inp / 1e6 * 240.218  # cache bucket is no longer free


def test_none_cache_model_prices_cache_write_at_input_rate():
    cost = compute_cost_rub(0, 0, 0, 1_000_000, _GIGACHAT3PRO)
    assert cost == pytest.approx(73.03, rel=1e-9)  # input rate, not 0


def test_published_cache_rate_is_kept():
    cost = compute_cost_rub(0, 0, 1_000_000, 0, _DS41FLASH)
    assert cost == pytest.approx(6.5, rel=1e-9)  # published rate, not input 64.94


# ---------------------------------------------------------------------------
# Resolver emits a distinguishing note
# ---------------------------------------------------------------------------

def test_resolver_notes_no_cache_tariff(cache_path, capsys):
    resolve_model_rates("MiniMaxAI/MiniMax-M3", cache_path=cache_path)
    err = capsys.readouterr().err
    assert "NOTE" in err and "INPUT rate" in err


def test_resolver_silent_for_published_cache_rate(cache_path, capsys):
    rates = resolve_model_rates("deepseek-ai/DeepSeek-V4.1-Flash", cache_path=cache_path)
    assert rates["cacheRead"] == pytest.approx(6.5)
    assert "NOTE" not in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Runner / backfill record the cache bucket explicitly
# ---------------------------------------------------------------------------

def _load_runner():
    spec = importlib.util.spec_from_file_location("oc_runner_cache_policy", ROOT / "run_openclaw_bench.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["oc_runner_cache_policy"] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_backfill():
    spec = importlib.util.spec_from_file_location("bcr_cache_policy", ROOT / "scripts" / "backfill_cost_rub.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bcr_cache_policy"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_runner_writes_explicit_cache_buckets(tmp_path):
    mod = _load_runner()
    out = tmp_path / "res.json"
    rows = [{
        "task_id": "t1", "passed": True, "elapsed_seconds": 1.0,
        "agent_input_tokens": 10, "agent_output_tokens": 5, "agent_total_tokens": 100,
    }]
    mod._write_results(rows, str(out), thinking="off",
                       command="python run_openclaw_bench.py --all")
    payload = json.loads(out.read_text())
    assert payload["summary"]["total_cache_read_tokens"] == 85  # 100 - 10 - 5
    assert payload["summary"]["total_cache_write_tokens"] == 0
    # derived per-task value stored explicitly too
    assert payload["tasks"][0]["agent_cache_read_tokens"] == 85


def test_backfill_derives_and_writes_cache_bucket(tmp_path, cache_path):
    mod = _load_backfill()
    art = tmp_path / "oc_shotlist_minimaxm3_off.json"
    art.write_text(json.dumps({
        "tasks": [],
        "summary": {
            "total_input_tokens": 10, "total_output_tokens": 5,
            "total_tokens": 100, "estimated_cost_rub": 0.0,
        },
    }), encoding="utf-8")
    changed = mod._recompute_file(art, dry_run=False, config_path="/nonexistent.json")
    assert changed is True
    s = json.loads(art.read_text())["summary"]
    assert s["total_cache_read_tokens"] == 85
    assert s["total_cache_write_tokens"] == 0
    expected = round(compute_cost_rub(10, 5, 85, 0, _MINIMAX), 2)
    assert s["estimated_cost_rub"] == pytest.approx(expected)


def test_backfill_prefers_explicit_bucket(tmp_path, cache_path):
    mod = _load_backfill()
    art = tmp_path / "oc_shotlist_minimaxm3_off.json"
    art.write_text(json.dumps({
        "tasks": [],
        "summary": {
            "total_input_tokens": 10, "total_output_tokens": 5, "total_tokens": 1_000_000,
            "total_cache_read_tokens": 42, "total_cache_write_tokens": 0,
            "estimated_cost_rub": 0.0,
        },
    }), encoding="utf-8")
    mod._recompute_file(art, dry_run=False, config_path="/nonexistent.json")
    s = json.loads(art.read_text())["summary"]
    # explicit bucket wins over the derived 1_000_000 - 10 - 5
    assert s["total_cache_read_tokens"] == 42
