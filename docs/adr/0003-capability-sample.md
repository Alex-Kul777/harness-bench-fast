# ADR-0003: Cost-bounded capability sample across the Medium waves (25%)

Date: 2026-11-06
Status: accepted
Context: The Medium waves (392–471: long 20, reflection 20, feasibility 40) are
heavy — the long wave reached ~20M tokens and ~2400 s per task, so running every
wave in full is expensive. We want a cheap but representative slice that includes
tasks models already solve and a few nobody solved, derivable from published
per-task outcomes rather than guessed. This is the Medium-wave analogue of the
Light Shot List (ADR-0001).

Decision: pick **20 tasks = 25% of 80**, stratified with **cost weighting** rather
than wave size, spanning the capability bands.

- Bands come from the published per-task outcomes across the available configs
  (codex + miniswe + claudecode `medium90`): ceiling = 3/3, boundary = 1–2/3,
  floor = 0/3. Labels are a proxy "by available configs".
- **Floor anchors: 3** (`392`, `403`, `398`), all in the long wave — the only wave
  with floor tasks. `407` is held as reserve.
- The **long quota is kept small** (don't inflate the most expensive wave); the
  remaining quota is filled from the cheaper reflection / feasibility waves
  (cost-weighted split long 3 / reflect 5 / feasibility 12).
- Cost control uses a **step cap** (primary) plus a **sanitary `--timeout`**;
  exact caps and whether to wire the step cap into the Pi runner are decided in a
  follow-up round (tracked separately, not fixed here).

Consequences:
  (+) Representative + discriminative subset at a fraction of full-run cost.
  (+) Floor anchors expose a real capability ceiling; ceiling anchors prove wiring.
  (-) All floor tasks live in the most expensive wave — an inherent tension.
  (-) A 20-task sample yields wide Wilson intervals; k = 1 gives no repeat
      significance.
  (risk) Band labels can move if the available config set changes.

Refs: `GLOSSARY.md` (Capability sample, Task band, Cost-weighted stratification),
`docs/medium90-results.json` + `docs/*-medium90-*.json` (per-task outcomes),
`scripts/build_fork_results.py` (umbrella suite `Medium (392–471)`).
