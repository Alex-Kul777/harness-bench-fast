"""gpt-5.5 published cache tariff (85.4 = input/10) is synthetic -> override to INPUT.

Change ``fix-gpt55-cache-rate-policy`` (Workboard ``803a4dc2``,
issue https://github.com/Alex-Kul777/openclaw-workspace/issues/446).

Cloud.ru bills gpt-5.5 as ``cost = input*854 + output*5124`` where ``input`` is the
FULL prompt including the cached prefix (verified +/-0.02% against the provider
export). The Cloud.ru catalog publishes ``cache_read = 85.4`` (= input/10), a
synthetic value that understates billing. Policy H2 is therefore extended: a
publicly published cache tariff that is synthetic/incorrect is overridden to the
INPUT rate through an explicit, auditable per-model table.

Red before the change, green after it. DeepSeek-V4.1-Flash (a genuine cache tariff
of 6.5) must stay untouched.
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

RATE_IN, RATE_OUT = 854.0, 5124.0
SYNTHETIC_CACHE = 85.4  # catalog's gpt-5.5 cache_read == input / 10

_CATALOG = {
    "fetched_at": "2026-11-10T00:00:00+00:00",
    "models": {
        "openai/gpt-5.5": {
            "input": RATE_IN, "output": RATE_OUT,
            "cache_read": SYNTHETIC_CACHE, "is_billable": True,
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
# Resolver: synthetic published cache rate is overridden to the INPUT rate
# ---------------------------------------------------------------------------

def test_gpt55_cache_rate_overridden_to_input(cache_path, capsys):
    rates = resolve_model_rates("openai/gpt-5.5", cache_path=cache_path)
    assert rates["cacheRead"] == pytest.approx(RATE_IN)
    err = capsys.readouterr().err
    assert "NOTE" in err and "override" in err.lower()


def test_gpt55_compound_provider_id_overridden(cache_path):
    rates = resolve_model_rates(
        "custom-foundation-models-api-cloud-ru/openai/gpt-5.5", cache_path=cache_path
    )
    assert rates["cacheRead"] == pytest.approx(RATE_IN)


def test_gpt55_published_85_4_is_not_used(cache_path):
    rates = resolve_model_rates("openai/gpt-5.5", cache_path=cache_path)
    assert rates["cacheRead"] != pytest.approx(SYNTHETIC_CACHE)


def test_gpt55_compute_cost_prices_cache_at_input(cache_path):
    rates = resolve_model_rates("openai/gpt-5.5", cache_path=cache_path)
    inp, out, cache = 3_079_431, 151_704, 7_555_456
    cost = compute_cost_rub(inp, out, cache, 0, rates)
    assert cost == pytest.approx(
        (inp + cache) / 1e6 * RATE_IN + out / 1e6 * RATE_OUT, rel=1e-9
    )
    assert cost == pytest.approx(9859.52, abs=0.01)  # published gpt-5.5 row


# ---------------------------------------------------------------------------
# DeepSeek genuine cache tariff is untouched
# ---------------------------------------------------------------------------

def test_deepseek_cache_rate_untouched(cache_path, capsys):
    rates = resolve_model_rates("deepseek-ai/DeepSeek-V4.1-Flash", cache_path=cache_path)
    assert rates["cacheRead"] == pytest.approx(6.5)
    assert "override" not in capsys.readouterr().err.lower()


def test_deepseek_cost_prices_cache_at_published_rate(cache_path):
    rates = resolve_model_rates("deepseek-ai/DeepSeek-V4.1-Flash", cache_path=cache_path)
    cost = compute_cost_rub(0, 0, 1_000_000, 0, rates)
    assert cost == pytest.approx(6.5, rel=1e-9)


# ---------------------------------------------------------------------------
# Backfill: gpt-5.5 rows (already cache@input) are NOT rolled back to 85.4
# ---------------------------------------------------------------------------

def _load_backfill():
    spec = importlib.util.spec_from_file_location(
        "bcr_gpt55_rate", ROOT / "scripts" / "backfill_cost_rub.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bcr_gpt55_rate"] = mod
    spec.loader.exec_module(mod)
    return mod


def _gpt55_summary():
    inp, out, cache = 3_079_431, 151_704, 7_555_456
    correct = round(
        compute_cost_rub(
            inp, out, cache, 0,
            {"input": RATE_IN, "output": RATE_OUT, "cacheRead": RATE_IN, "cacheWrite": 0.0},
        ),
        2,
    )
    return inp, out, cache, correct


def test_backfill_does_not_rollback_gpt55(tmp_path, cache_path):
    mod = _load_backfill()
    inp, out, cache, correct = _gpt55_summary()
    art = tmp_path / "oc_medium_feasibility_gpt55_off_20261110.json"
    art.write_text(json.dumps({
        "model": "custom-foundation-models-api-cloud-ru/openai/gpt-5.5",
        "tasks": [],
        "summary": {
            "total_input_tokens": inp, "total_output_tokens": out,
            "total_tokens": inp + out + cache,
            "total_cache_read_tokens": cache, "total_cache_write_tokens": 0,
            "estimated_cost_rub": correct,
        },
    }), encoding="utf-8")
    changed = mod._recompute_file(art, dry_run=False, config_path="/nonexistent.json")
    assert changed is False, "backfill must not rewrite a correct cache@input gpt-5.5 cost"
    assert json.loads(art.read_text())["summary"]["estimated_cost_rub"] == pytest.approx(correct)


def test_backfill_would_fix_a_synthetic_billed_gpt55_row(tmp_path, cache_path):
    """A row wrongly billed at the synthetic 85.4 cache rate is corrected to cache@input."""
    mod = _load_backfill()
    inp, out, cache, correct = _gpt55_summary()
    understated = round(
        inp / 1e6 * RATE_IN + out / 1e6 * RATE_OUT + cache / 1e6 * SYNTHETIC_CACHE, 2
    )
    assert understated < correct
    art = tmp_path / "oc_shotlist_gpt55_off_20261110.json"
    art.write_text(json.dumps({
        "model": "openai/gpt-5.5",
        "tasks": [],
        "summary": {
            "total_input_tokens": inp, "total_output_tokens": out,
            "total_tokens": inp + out + cache,
            "total_cache_read_tokens": cache, "total_cache_write_tokens": 0,
            "estimated_cost_rub": understated,
        },
    }), encoding="utf-8")
    changed = mod._recompute_file(art, dry_run=False, config_path="/nonexistent.json")
    assert changed is True
    assert json.loads(art.read_text())["summary"]["estimated_cost_rub"] == pytest.approx(correct)
