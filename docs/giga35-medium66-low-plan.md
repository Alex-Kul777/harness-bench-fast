# GigaChat 3.5 Reasoning (low) — Medium-66 on Pi (plan)

## Goal
Run **GigaChat 3.5 Reasoning** at **`low`** on the **same 66 Medium tasks** our
Pi·DeepSeek-V4.1-Flash Medium coverage used, so the two are directly comparable
(same denominator, same tasks) → a second `ours` row on the **Medium sample** tab.

## Task set — the 66 (= our DeepSeek coverage)
| wave | tasks | source run files (DeepSeek) | timeout floor |
|---|---:|---|---:|
| long | 6 | `pi_long_ds41flash_20261106` + `pi_pilot_long3_20261105` | 7200 s |
| reflect | 20 | `pi_reflect_ds41flash_20261106` + `_b` | 1800 s |
| feasibility | 40 | `wave19_full_ds41flash` | 3600 s |
| **total** | **66** | | |

DeepSeek reference on the same 66: **55/66** (long 3/6 · reflect 16/20 · feasibility 36/40).

## Run
```bash
cd ~/.openclaw/workspace/projects/benchmark-research
bash harness-bench-fast/scripts/run_giga35_medium66_low.sh        # LVL=low CONC=3
```
- **3 per-wave invocations** (a single `--timeout` can't cover 1800/3600/7200 floors).
- Model `ai-sage/GigaChat3.5-432B-A28B-Reasoning`, `--thinking low`, concurrency **3**.
- Outputs: `results/pi_medium_{long,reflect,feasibility}_giga35_low_<date>.json`
  (wave token in the stem → aggregates into a Medium row).

## Cost / time estimate (rough)
- DeepSeek durations: long mean ~4.1 ks (max 7.3 ks) · reflect ~0.5 ks · feas ~0.26 ks.
- At concurrency 3: long ≈ 6·4.1k/3 ≈ 2.3 h, reflect ≈ 0.9 h, feas ≈ 1 h → **≈ 4–5 h wall**.
- Token cost is the open risk: Medium tasks are long-context, so spend will far exceed the
  shot list (which was 356 ₽ at `low`). Expect **hundreds–low-thousands ₽**; track via status files.

## Status / watch
`/tmp/pi_giga35_medium_{long,reflect,feasibility}_status.json` + logs `/tmp/pi_giga35_medium_*.log`.

## Publish follow-up (after the run, not now)
A Medium row needs the Medium (wave) generator path, which today **lacks two things**:
1. `build_fork_pages.py` `MODEL_TOKENS` has **no `giga35`** → the row is skipped ("unresolved model").
2. `build_fork_pages.py` `classify_profile` has **no reasoning-level handling** → a `low` arm
   publishes with a **blank profile** (this is exactly the `fork-doc-layering` gap).
So publishing requires adding the `giga35` token + a `low`-aware level suffix to
`build_fork_pages.py`, then regenerate with checks. Deferred to publish time.

## Risks
- **Long wave is heavy** (~2 h tasks); if a task times out it's a normal fail, not infra.
- **Truncation**: `low` reasons less than `high`, so risk is low; the model cap is 32768.
- **Comparability**: run on the currently checked-out commit; don't merge upstream first.
