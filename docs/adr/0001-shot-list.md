# ADR-001: Benchmark Shot List (v1)

Date: 2026-08-12
Status: accepted
Context: The full 391-task benchmark takes 15-35 minutes per run. Analysis of 12 published runs (6 strong models: Pi GLM-5.2, Kimi K3, OpenClaw GLM-5.2, opencode GLM-5.2, Hermes GLM-5.2, Claude Haiku; 6 weak models: GigaChat 3.5 pure, Qwen3-Coder-30B, GigaChat 3 Pro, GPT-OSS-20B, GPT-OSS-120B, GigaChat 3 Lightning) showed that only 34/391 tasks have universal pass (zero discrimination). The remaining 357 tasks discriminate between model/harness combos.

Decision: Create a stratified shot list of 52 tasks (~13% of 391) that preserves wave coverage and prioritizes discrimination power.

Composition:
- 5 smoke tasks (universal-pass, 1 per major wave): verify model works at all
- 18 high-discrimination tasks (<50% pass rate): the most informative tasks
- 25 mid-discrimination tasks (50-89% pass, ~2 per wave, lowest rates first)
- 4 low-discrimination tasks (90-99% pass, 1 per major wave): regression detection

Selection method:
- Stratified by wave (13 waves) to guarantee capability coverage
- Within each stratum, sorted by ascending pass rate (hardest first)
- High-discrim tasks all included regardless of wave

Consequences:
  - (+) Runtime drops from ~35 min to ~4-7 min (7-10x speedup)
  - (+) Preserves all 13 wave capabilities (core through CLI-composition)
  - (+) All 18 highest-discrimination tasks included — maximum information per minute
  - (+) Smoke tasks catch catastrophic regressions (model produces nothing)
  - (-) 89 low-discrim tasks excluded — rare failures on these won't be caught
  - (-) 250 mid-discrim tasks reduced to 25 — some model-specific failures missed
  - (-) Not directly comparable to full-run pass rates (different denominator)
  - (risk) Shot list may need refresh if task-set version bumps change task semantics

Refresh policy: Re-evaluate at each task-set version bump (0.17.0, 0.18.0...). Between versions, shot list is stable.

Analysis data: 12 runs on task-set v0.16.0, available in runs/ directory.
