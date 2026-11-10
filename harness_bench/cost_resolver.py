"""Per-model ₽ pricing resolver for harness-bench-fast runners.

Resolves cost rates (input / output / cacheRead / cacheWrite ₽ per 1M tokens)
for a given model id, in this order of precedence:

1. the Cloud.ru catalog cache (``~/.openclaw/cloudru-prices.json``, populated by
   ``scripts/sync_cloudru_prices.py``; override with ``$CLOUDRU_PRICES_CACHE``),
2. the ``cost`` block in ``~/.openclaw/openclaw.json`` (or ``$OPENCLAW_CONFIG``),
3. an explicit documented fallback (GLM-5.2: 239.12 / 751.52 / 0 / 0) with a
   WARNING on stderr -- never silent.

A missing ``cache_read`` field in a source is treated as 0.
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
_DEFAULT_CACHE_PATH = Path.home() / ".openclaw" / "cloudru-prices.json"

# Filename/family -> canonical model id. Used as a LAST resort (before the GLM-5.2
# fallback) when an artifact exposes no model field at all. Ordered: first match wins.
# Keep this list small and explicit -- add a family only when its canonical id is
# known and resolvable by this resolver.
_FILENAME_MODEL_HINTS: tuple[tuple[str, str], ...] = (
    ("gigachat3pro", "GigaChat/GigaChat-3-Pro"),
    ("giga35", "ai-sage/GigaChat3.5-432B-A28B-Reasoning"),
    ("glm52", "zai-org/GLM-5.2"),
    ("glm53", "zai-org/GLM-5.3"),
    ("qwen36", "Qwen/Qwen3.6-35B-A3B"),
    ("oss120b", "openai/gpt-oss-120b"),
    ("minimaxm3", "MiniMaxAI/MiniMax-M3"),
    ("ds41flash", "deepseek-ai/DeepSeek-V4.1-Flash"),
)


def model_hint_from_filename(filename: Optional[str]) -> Optional[str]:
    """Infer a canonical model id from an artifact filename/stem, or None.

    Matches the artifact stem case-insensitively against ``_FILENAME_MODEL_HINTS``;
    the first matching token wins. This never overrides an explicit model id -- it is
    only consulted by :func:`resolve_model_rates` when the given ``model_id`` yields
    no rates.
    """
    if not filename:
        return None
    stem = Path(filename).stem.lower()
    for token, model_id in _FILENAME_MODEL_HINTS:
        if token in stem:
            return model_id
    return None


def _load_json(path: Path, what: str) -> dict:
    """Load a JSON file; return empty dict on any read/parse error."""
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except Exception as exc:  # noqa: BLE001
        print(f"[cost_resolver] WARNING: could not read {what} {path}: {exc}", file=sys.stderr)
        return {}


def _load_config(config_path: Optional[str | Path] = None) -> dict:
    """Load openclaw.json; return empty dict on any error."""
    path = Path(config_path or os.environ.get("OPENCLAW_CONFIG", "") or _DEFAULT_CONFIG_PATH)
    return _load_json(path, "config")


def _catalog_cache_path(cache_path: Optional[str | Path] = None) -> Path:
    return Path(
        cache_path or os.environ.get("CLOUDRU_PRICES_CACHE", "") or _DEFAULT_CACHE_PATH
    ).expanduser()


def _load_catalog_cache(cache_path: Optional[str | Path] = None) -> dict:
    """Return the ``models`` mapping of the catalog cache, or {} if unavailable."""
    path = _catalog_cache_path(cache_path)
    data = _load_json(path, "catalog cache")
    models = data.get("models")
    return models if isinstance(models, dict) else {}


def _rates_from_cache(model_id: str, cache: dict) -> Optional[dict]:
    """Return rates for *model_id* from the catalog cache, or None.

    Matches the full model id exactly, or via suffix when the runner passes a
    compound ``<provider>/<model>`` id that ends with the catalog entry id.
    """
    if not cache:
        return None
    entry = cache.get(model_id)
    if entry is None:
        for key, value in cache.items():
            if model_id == key or model_id.endswith("/" + str(key)):
                entry = value
                break
    if not isinstance(entry, dict):
        return None
    return {
        "input": float(entry.get("input") or 0.0),
        "output": float(entry.get("output") or 0.0),
        # a missing cache_read field is treated as 0
        "cacheRead": float(entry.get("cache_read") or 0.0),
        "cacheWrite": 0.0,
    }


def _rates_from_config(model_id: str, cfg: dict) -> Optional[dict]:
    """Return rates for *model_id* from openclaw.json ``cost`` blocks, or None."""
    providers: dict = (cfg.get("models") or {}).get("providers") or {}
    for provider_name, provider_data in providers.items():
        if not isinstance(provider_data, dict):
            continue
        for entry in provider_data.get("models") or []:
            if not isinstance(entry, dict):
                continue
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
    return None


def resolve_model_rates(
    model_id: str,
    config_path: Optional[str | Path] = None,
    cache_path: Optional[str | Path] = None,
    filename: Optional[str] = None,
) -> dict:
    """Return cost rates dict for *model_id*.

    Returns a dict with keys: input, output, cacheRead, cacheWrite  (₽/1M tokens).

    Resolution order:

    1. catalog cache entry for the model (populated from the live Cloud.ru catalog),
    2. ``cost`` block in openclaw.json (matched against ``<provider>/<model>``),
    3. *last resort* -- a canonical model id inferred from the artifact
       *filename* via :func:`model_hint_from_filename` (re-resolved through 1-2),
    4. GLM-5.2 fallback rates with a WARNING on stderr.

    An explicit ``model_id`` always wins over the filename hint.
    """
    cache = _load_catalog_cache(cache_path)
    if model_id:
        rates = _rates_from_cache(model_id, cache)
        if rates is not None:
            return rates

    cfg = _load_config(config_path)
    if model_id:
        rates = _rates_from_config(model_id, cfg)
        if rates is not None:
            return rates

    # Last resort before the documented fallback: infer the model from the artifact
    # filename. Never silent -- warn that the model was guessed.
    hint = model_hint_from_filename(filename)
    if hint:
        rates = _rates_from_cache(hint, cache)
        if rates is None:
            rates = _rates_from_config(hint, cfg)
        if rates is not None:
            print(
                f"[cost_resolver] WARNING: no cost rates for model "
                f"'{model_id or '(none)'}' (checked catalog cache and config); "
                f"inferred '{hint}' from filename '{filename}'.",
                file=sys.stderr,
            )
            return rates

    print(
        f"[cost_resolver] WARNING: no cost rates found for model '{model_id}' "
        f"(checked catalog cache and config). Using GLM-5.2 fallback rates "
        f"(239.12/751.52/0/0 ₽/1M).",
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
