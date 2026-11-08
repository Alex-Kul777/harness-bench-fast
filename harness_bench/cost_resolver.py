"""Per-model ₽ pricing resolver for harness-bench-fast runners.

Reads ~/.openclaw/openclaw.json (or $OPENCLAW_CONFIG) and resolves cost
rates (input / output / cacheRead / cacheWrite ₽ per 1M tokens) for a
given model id.

Fallback (logged to stderr): GLM-5.2 rates (239.12 / 751.52 / 0 / 0).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

# Default fallback rates (GLM-5.2 / Cloud.ru, August 2026)
_FALLBACK_RATES: dict = {
    "input": 239.12,
    "output": 751.52,
    "cacheRead": 0.0,
    "cacheWrite": 0.0,
}

_DEFAULT_CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"


def _load_config(config_path: Optional[str | Path] = None) -> dict:
    """Load openclaw.json; return empty dict on any error."""
    path = Path(config_path or os.environ.get("OPENCLAW_CONFIG", "") or _DEFAULT_CONFIG_PATH)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except Exception as exc:  # noqa: BLE001
        print(f"[cost_resolver] WARNING: could not read {path}: {exc}", file=sys.stderr)
        return {}


def resolve_model_rates(
    model_id: str,
    config_path: Optional[str | Path] = None,
) -> dict:
    """Return cost rates dict for *model_id*.

    Returns a dict with keys: input, output, cacheRead, cacheWrite  (₽/1M tokens).

    The *model_id* is matched against the compound key ``<provider>/<model>`` stored
    in openclaw.json under ``models.providers.<provider>.models[].id``.

    If the model is not found, falls back to GLM-5.2 rates and prints a warning.
    """
    cfg = _load_config(config_path)
    providers: dict = (cfg.get("models") or {}).get("providers") or {}

    for provider_name, provider_data in providers.items():
        if not isinstance(provider_data, dict):
            continue
        for entry in provider_data.get("models") or []:
            if not isinstance(entry, dict):
                continue
            # entry.id may be just the model name; compound key is provider/entry_id
            entry_id: str = entry.get("id", "")
            compound = f"{provider_name}/{entry_id}"
            if model_id == compound or model_id == entry_id:
                cost = entry.get("cost")
                if isinstance(cost, dict):
                    return {
                        "input": float(cost.get("input") or 0.0),
                        "output": float(cost.get("output") or 0.0),
                        "cacheRead": float(cost.get("cacheRead") or 0.0),
                        "cacheWrite": float(cost.get("cacheWrite") or 0.0),
                    }

    print(
        f"[cost_resolver] WARNING: no cost rates found for model '{model_id}'. "
        f"Using GLM-5.2 fallback rates (239.12/751.52/0/0 ₽/1M).",
        file=sys.stderr,
    )
    return dict(_FALLBACK_RATES)


def compute_cost_rub(
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int,
    cache_write_tokens: int,
    rates: dict,
) -> float:
    """Compute ₽ cost from token counts and per-model rates."""
    return (
        input_tokens / 1_000_000 * rates["input"]
        + output_tokens / 1_000_000 * rates["output"]
        + cache_read_tokens / 1_000_000 * rates["cacheRead"]
        + cache_write_tokens / 1_000_000 * rates["cacheWrite"]
    )
