# add-pi-runner-task-timeout-floors — proposal

## Why

The Pi runner passes its `--timeout` straight to the container and **ignores the
task's `min_timeout_seconds` / `max_timeout_seconds`**. The frozen task set carries
floors (long **7200**, reflection **1800**, wave19 **3600/3600**), and upstream runs
use the same rule ("timeout 900 s, with task-specific floors of 7200 s for the long
wave and 1800 s for reflection"). Ignoring floors makes our results
**non-comparable** and can cut a long task below its floor — an unfair fail. The
accepted timeout-only policy (ADR-0004) makes this the single limiting mechanism, so
it must match the frozen protocol.

## What Changes

- Pi runner resolves the per-task timeout with the shared
  `effective_task_timeout(configured, min_timeout_seconds, max_timeout_seconds)`
  (`max(configured, min)`, clamped by `max`) instead of a raw value.
- The effective timeout is exported to the container (`HBF_TASK_TIMEOUT_SECONDS`)
  and recorded per task in the run JSON.
- Per-wave default timeouts follow the frozen set: long 7200 / reflection 1800 /
  feasibility 3600; ordinary tasks 900.
- A timeout **below a task floor** is refused-by-default; a deliberate
  cost-cap below the floor is allowed only with an explicit opt-in and is recorded
  as `non_comparable`.

Not **BREAKING**: default `--timeout` unchanged; the floor only *raises* an
explicitly finite value, matching `effective_task_timeout`.

## Capabilities

- **New Capabilities**: — (none)
- **Modified Capabilities**: `benchmark-runs` — adds the effective-timeout
  requirement (delta spec).

## Out of scope

- Resource budgets **inside** tasks (unchanged).
- A work/step bound (see ADR-0004; not available in `pi-agent`).

## Impact

- `run_pi_bench.py` (timeout resolution, env, JSON field).
- `tests/` — a clamp/floor regression test.
- Task data and upstream layer untouched.

## Tracking

- Workboard: `acc1f966` (board project-a)
- Epic: #433 (relates to #432)
