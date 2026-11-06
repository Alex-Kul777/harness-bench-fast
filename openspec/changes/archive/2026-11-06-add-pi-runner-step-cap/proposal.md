# add-pi-runner-step-cap — proposal

## Why (обновлено после feasibility)

Cost of a run scales with **steps × context**, so long 500+-step tasks dominate
spend. The deepagents runner supports a step cap (`recursion_limit`), and we wanted
the same on the Pi runner. **Feasibility check found the underlying `pi-agent`
(bundled `@earendil-works/pi-coding-agent` v1.5.0 in `pi-sandbox:latest`) exposes
NO step / recursion / turn limit** — no flag, no dist code path, no env fallback.
A step cap therefore **cannot** be wired without emulation.

## What Changes (decision: timeout-only)

- **No behavioural change.** The Pi runner keeps `--timeout` as its **only**
  limit. We do **not** emulate a step cap (no fake flag, no silent substitution).
- The limitation is documented so future work does not re-attempt the impossible
  wiring blindly.

Not **BREAKING**: adds no code; documents an accepted limitation.

## Capabilities

- **New Capabilities**: — (none)
- **Modified Capabilities**: `benchmark-runs` — documents that the Pi runner relies
  on the sanitary timeout because the agent exposes no step cap (delta spec).

## Out of scope

- Emulating a step cap inside the runner.
- An external step cap (monitor NDJSON, kill on threshold) — a distinct future
  change, not decided here.
- Routing cost-bounded runs through the deepagents runner (it does support a cap).

## Impact

- Documentation only: `benchmark-runs` spec (this delta) + ADR-0004.
- `run_pi_bench.py` unchanged.

## Tracking

- Workboard: `0d0015f6` (board project-a)
- Epic: #432
