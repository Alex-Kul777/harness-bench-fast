# ADR-001: Shot List for harness-bench-fast
Date: 2026-08-12
Status: accepted

## Context

The full 391-task benchmark takes 15-35 minutes per run. With 12+ published
runs across 10+ model/harness combinations, we now have enough data to
identify tasks with zero discriminative power and build a reduced "shot list"
for fast iteration.

Analysis of 12 full v0.16.0 runs (GigaChat 3.5 pure, Qwen3-Coder-30B,
GigaChat 3 Pro, GPT-OSS-20B, GPT-OSS-120B, GigaChat 3 Lightning, Claude
Haiku 4.5, DeepSeek V4 Flash, Kimi K3, opencode GLM-5.2, OpenClaw GLM-5.2,
Hermes GLM-5.2) revealed:

- **34 tasks** (8.7%) — universal pass (all 12 runs): zero discrimination
- **89 tasks** (22.8%) — low discrim (90-99% pass): rare failures
- **250 tasks** (64%) — mid discrim (50-89% pass): core discrimination
- **18 tasks** (4.6%) — high discrim (<50% pass): strongest discriminators

## Decision

Build a **53-task stratified shot list** covering all 13 waves:

| Stratum | Count | Selection rule |
|---|---|---|
| Smoke (universal pass) | 5 | 1 per major wave group, simplest task |
| High discrim (<50%) | 18 | All included — highest information value |
| Mid discrim (50-89%) | 26 | 2 per wave, lowest pass rate first |
| Low discrim (90-99%) | 4 | 1 per major wave group, regression detection |

Total: **53 tasks** (~13.6% of 391). Estimated runtime: 4-7 min vs 15-35 min.

## Consequences

### Positive
- **7-10x faster** iteration for model comparison and regression testing
- **Preserves wave coverage**: all 13 waves represented
- **Maximises information**: all 18 highest-discrimination tasks included
- **Smoke floor**: 5 universal-pass tasks catch basic breakage
- **Reproducible**: fixed list in `shot_list.txt`, versioned with task-set

### Negative
- **Reduced confidence**: 53 tasks cannot detect regressions in the 338
  excluded tasks. A model could pass all 53 but fail on an excluded task.
- **Skewed toward hard tasks**: 18/53 (34%) are high-discrim, so pass
  rates on the shot list will be lower than on the full 391-task set.
  Shot list pass rates are NOT comparable to full-run pass rates.
- **Stale risk**: if task-set semantics change (v0.17.0+), the shot list
  must be recomputed. Mitigated by versioning with task-set bumps.

### Risks
- A model that optimises for the shot list's task distribution may
  overperform on hard tasks while underperforming on common tasks.
  Mitigated by keeping 5 smoke + 4 low-discrim tasks.
- The 34 universal-pass tasks may become discriminative if future models
  are weaker. Mitigated by recomputing on each task-set version bump.

## Selection Method

1. Load all available v0.16.0 full-run JSONs (12 runs, 10+ model/harness combos)
2. For each task, compute pass rate across all runs
3. Classify: universal (100%), low (90-99%), mid (50-89%), high (<50%)
4. Stratify by wave (13 waves), select per stratum rules above
5. Sort by task number for readability

## Maintenance

- **Recompute on every task-set version bump** (v0.17.0, v0.18.0, ...)
- Between versions, the shot list is frozen
- Full 391-task run remains the canonical benchmark for published results
- Shot list is for fast iteration, regression detection, and model comparison
