# add-fork-duration-column — proposal

## Why

The owner wants to see **how long tasks actually take** and how **our Pi run
compares to Codex / mini-SWE / Claude** by time. Upstream publishes per-task
times only in data (`docs/<model>-medium90-*.json` → `outcomes[].elapsed_seconds`),
not in any wave table, and our fork page shows no Duration at all. We should surface
it on `docs/fork-medium90.html` with an explicit per-task join to the upstream
measurements.

## What Changes

- `scripts/build_fork_pages.py` reads per-task `elapsed_seconds` from our run
  files and from the upstream medium90 measurements, and writes two new blocks:
  - `rows[].suites[<wave>].duration = {n, mean, median, max}` (our runs, seconds);
  - `duration_by_wave`: for each wave, the mean/median/max per configuration —
    `Pi (ours)` plus `Codex + DeepSeek`, `mini-SWE + DeepSeek`,
    `Claude Code + Sonnet`.
- `docs/fork-medium90.html` + `docs/fork-results.js` render a **Duration** column in
  the per-config table and a new **Duration by wave** table.
- Additive only: existing JSON keys and columns are unchanged.

## Capabilities

- **New Capabilities**: — (none)
- **Modified Capabilities**: `result-reporting` — adds the duration data + column
  requirement (delta spec).

## Out of scope

- Per-task time for **every** wave on our side (we only measured a subset).
- Changing the upstream files; we read them, never write.
- The runner change (separate change `add-pi-runner-task-timeout-floors`).

## Impact

- `scripts/build_fork_pages.py`, `docs/fork-results.js`, `docs/fork-medium90.html`,
  `docs/fork-medium90-results.json` (regenerated).
- No upstream files touched; markdown canonical-column lint unaffected.

## Tracking

- Workboard: `3c524036` (board project-a)
- Epic: #434
