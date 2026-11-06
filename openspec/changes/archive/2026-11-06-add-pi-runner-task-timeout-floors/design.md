# add-pi-runner-task-timeout-floors — design

## Context

`harness_bench/core.py`:
```
def effective_task_timeout(configured_seconds, min_timeout_seconds=None, max_timeout_seconds=None):
    timeout = max(configured_seconds, min_timeout_seconds or 0.0)
    return min(timeout, max_timeout_seconds) if max_timeout_seconds is not None else timeout
```
Task floors in the frozen set: long `392/398/403` min **7200**; reflection
`415/422/426/430` min **1800**; feasibility `432` min=max **3600**. Upstream uses a
base **900 s** with the same floors; wave19 documents a **3600 s** sanitary guard.

`run_pi_bench.py` today: `DEFAULT_TIMEOUT = 660`, `--timeout` → container directly;
no floors, no `HBF_TASK_TIMEOUT_SECONDS`, no field in the JSON.

## Decisions

1. **Resolve with the shared helper.** In `run_one_task`, compute
   `eff = effective_task_timeout(timeout, task.min_timeout_seconds,
   task.max_timeout_seconds)` (import from `harness_bench.core` /
   `harness_bench.runtime_limits`). Use `eff` for the process timeout, the
   container kill, and the JSON.
2. **Per-wave defaults.** Keep `--timeout` as the caller value; document the frozen
   defaults (long 7200 / reflect 1800 / feasibility 3600 / ordinary 900). Because
   the floor raises, a single low `--timeout` still yields the right per-task value.
3. **Record it.** Add `"timeout": eff` to each task record and a
   `"timeout"` note in `summary`; export `-e HBF_TASK_TIMEOUT_SECONDS={eff}`.
4. **Below-floor guard.** If `--timeout` is finite and `< task.min_timeout_seconds`
   and no explicit `--allow-below-floor` opt-in is given, **raise/skip** that task
   (do not silently under-cut). With the opt-in, run and mark
   `"comparable": false` (or `timeout_capped: true`).
5. **Keep kill-by-name.** The existing container `docker kill` on expiry stays.

## Unit / semantics

- A **graph step** is not a model or service call (README). Timeout is wall-clock
  host-measured agent execution.
- Upstream wave19: a timely host-recorded `submit`/`finish` that passes the verifier
  earns credit even if the reply/process later times out. Our comparison tables
  should keep that nuance in prose, not re-encode it.

## Risks

- Raising long to 7200 makes long runs **expensive** (up to 2 h/task). That is the
  cost of comparability; a cheaper run is a labelled deviation (decision 4).
- Floors may differ across task-set versions → read them from the task, never
  hard-code.
