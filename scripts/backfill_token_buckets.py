#!/usr/bin/env python3
"""Recompute token buckets for result artifacts produced by the pre-fix runners.

Two defects are repaired (see change ``fix-bench-token-accounting``):

1. **Pi over-count (x3).** ``run_pi_bench._extract_usage`` used to recursively
   scan the whole ``--mode json`` stream, so the *same* assistant ``usage``
   object was counted once from ``message_end``, again from ``turn_end`` and
   again from ``agent_end.messages[]`` (only ``message_update`` deltas were
   skipped).  The stored ``agent_*_tokens`` are therefore ``3x`` the truth.
   The true bucket is ``stored / 3``; the dropped cache-read bucket is
   ``(total - input - output) / 3`` (Pi ``total = input + output + cacheRead``).

2. **OpenClaw cache derivation.**  The runner stored ``agent_total_tokens``
   (envelope ``usage.total``, invariant ``total = input + output + cacheRead +
   cacheWrite``) but re-derived the cache bucket instead of reading the
   envelope's explicit ``cacheRead``/``cacheWrite``.  Here the true cache-read
   bucket is ``total - input - output``.

``estimated_cost_rub`` is recomputed through the shared cost resolver.  For
gpt-5.5 the provider export proves cached input is billed at the **input** rate
(``cost = input_tokens*854 + output_tokens*5124``), so the cache bucket is
priced at the input rate for that model.

Usage:
    python3 scripts/backfill_token_buckets.py [results_dir] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from harness_bench.cost_resolver import compute_cost_rub, resolve_model_rates  # noqa: E402

# Models whose provider billing prices cached input at the INPUT rate (verified
# against the Cloud.ru provider export), overriding a catalog cache tariff that
# is not actually charged separately.
_CACHE_AT_INPUT_RATE = ("gpt-5.5",)


def _billing_rates(model: str, rates: dict) -> dict:
    if any(tok in (model or "") for tok in _CACHE_AT_INPUT_RATE):
        return {"input": rates["input"], "output": rates["output"]}  # cache -> input rate
    return rates


def _third(x) -> int:
    return int(round((x or 0) / 3.0))


def _fix_pi_task(t: dict) -> None:
    """Pi task entry: undo the x3 over-count and recover the cache bucket."""
    old_in = int(t.get("agent_input_tokens") or 0)
    old_out = int(t.get("agent_output_tokens") or 0)
    old_tok = int(t.get("agent_total_tokens") or 0)
    t["agent_input_tokens"] = _third(old_in)
    t["agent_output_tokens"] = _third(old_out)
    t["agent_reasoning_tokens"] = _third(t.get("agent_reasoning_tokens"))
    t["agent_total_tokens"] = _third(old_tok)
    t["agent_cache_read_tokens"] = max(_third(old_tok) - _third(old_in) - _third(old_out), 0)
    t["agent_cache_write_tokens"] = 0
    if "agent_api_calls" in t:
        t["agent_api_calls"] = _third(t.get("agent_api_calls"))
        t["agent_steps"] = t["agent_api_calls"]
    if "agent_tool_calls" in t:
        t["agent_tool_calls"] = _third(t.get("agent_tool_calls"))


def _fix_oc_task(t: dict) -> None:
    """OpenClaw task entry: keep buckets, add the explicit cache-read bucket."""
    cr = t.get("agent_cache_read_tokens")
    if cr is None or int(cr or 0) == 0:
        derived = max(
            int(t.get("agent_total_tokens") or 0)
            - int(t.get("agent_input_tokens") or 0)
            - int(t.get("agent_output_tokens") or 0),
            0,
        )
        t["agent_cache_read_tokens"] = derived
    t["agent_cache_write_tokens"] = int(t.get("agent_cache_write_tokens") or 0)


def _recompute(path: Path, *, dry_run: bool) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    harness = data.get("harness") or ("pi" if path.name.startswith("pi_") else "openclaw")
    tasks = data.get("results") if isinstance(data.get("results"), list) else data.get("tasks")
    summary = data.get("summary")
    if not isinstance(tasks, list) or not isinstance(summary, dict):
        print(f"  SKIP {path.name}: no task list / summary")
        return False

    model = data.get("model") or summary.get("model") or ""
    for t in tasks:
        if not isinstance(t, dict):
            continue
        (_fix_pi_task if harness == "pi" else _fix_oc_task)(t)

    total_in = sum(int(t.get("agent_input_tokens") or 0) for t in tasks)
    total_out = sum(int(t.get("agent_output_tokens") or 0) for t in tasks)
    total_re = sum(int(t.get("agent_reasoning_tokens") or 0) for t in tasks)
    total_cr = sum(int(t.get("agent_cache_read_tokens") or 0) for t in tasks)
    total_cw = sum(int(t.get("agent_cache_write_tokens") or 0) for t in tasks)
    total_tok = sum(int(t.get("agent_total_tokens") or 0) for t in tasks)
    total_steps = sum(int(t.get("agent_steps") or 0) for t in tasks)
    rates = _billing_rates(model, resolve_model_rates(model))
    cost = round(compute_cost_rub(total_in, total_out, total_cr, total_cw, rates), 2)

    summary.update({
        "total_input_tokens": total_in,
        "total_output_tokens": total_out,
        "total_reasoning_tokens": total_re,
        "total_cache_read_tokens": total_cr,
        "total_cache_write_tokens": total_cw,
        "total_tokens": total_tok,
        "total_steps": total_steps,
        "estimated_cost_rub": cost,
    })
    if harness == "pi":
        summary["total_tool_calls"] = sum(int(t.get("agent_tool_calls") or 0) for t in tasks)

    print(f"  {path.name}: in={total_in} out={total_out} cr={total_cr} -> {cost:.2f} ₽")
    if not dry_run:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results_dir", nargs="?", default="results")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--glob", default="*gpt55*20261110.json")
    args = ap.parse_args()
    d = Path(args.results_dir)
    files = sorted(d.glob(args.glob))
    if not files:
        print(f"no files matching {args.glob} in {d}")
        return
    print(f"=== backfill_token_buckets ({'DRY RUN' if args.dry_run else 'REWRITING'}) — {len(files)} files ===")
    for f in files:
        _recompute(f, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
