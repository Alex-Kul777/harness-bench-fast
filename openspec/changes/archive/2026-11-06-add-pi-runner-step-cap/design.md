# add-pi-runner-step-cap — design

## Context

`harness_bench/runtime_limits.py` supports a step cap (`recursion_limit`, graph
supersteps; 0 = unlimited) for the deepagents path, and `run_pi_bench.py` exposes
only `--timeout` / `--concurrency` for Pi.

## Finding (from the feasibility step)

The bundled agent has **no step/recursion/turn control**:
- `docker run --rm pi-sandbox:latest --help` has no `--recursion-limit`,
  `--max-steps`, `--step-limit`, `--max-turns`, `--max-iterations`.
- Dist flag inventory: only `--max-depth`, `--max-results`, `--timeout` are
  limit-ish; none govern agent steps.
- Dist code grep for `maxSteps|maxTurns|stepLimit|recursionLimit|maxIterations`
  (excluding `node_modules`) → no matches. (The sole `recursionLimit` is inside
  bundled `protobufjs` — a protobuf nesting guard for `--max-depth`, unrelated.)
- No `PI_*` env var governs steps → `HBF_TASK_RECURSION_LIMIT` cannot be honoured.

## Decision (a): timeout-only

1. **Do not emulate.** No synthetic step counter, no killing on a fabricated
   threshold inside the runner under this change.
2. **Pi keeps `--timeout`** (`DEFAULT_TASK_TIMEOUT_SECONDS = 3600`; per-wave
   invocation values in ADR-0004) as its only limit. Unchanged behaviour.
3. **Record the limitation** here and in ADR-0004 so it is not re-attempted.
4. Target caps from ADR-0004 (long 600 / feasibility 150 / reflect 60) remain the
   desired values **if** a future change provides a real mechanism.

## Future options (out of scope, for a separate change)

- External cap: read `/tmp/pi_bench_out_*.ndjson`, count `message_end` turns, kill
  the container on a threshold — deterministic, no agent support needed.
- Use deepagents (has `recursion_limit`) for cost-bounded runs.
