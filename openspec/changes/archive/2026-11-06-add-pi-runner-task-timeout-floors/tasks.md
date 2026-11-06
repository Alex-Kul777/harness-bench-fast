# add-pi-runner-task-timeout-floors — tasks

## 1. Реализация

- [x] 1.1 Import `effective_task_timeout` (and constants) into `run_pi_bench.py`
- [x] 1.2 Resolve `eff = effective_task_timeout(--timeout, task.min_timeout_seconds, task.max_timeout_seconds)` in `run_one_task`; use `eff` for the process timeout and container kill
- [x] 1.3 Export `-e HBF_TASK_TIMEOUT_SECONDS={eff}`; record `"timeout": eff` per task and in `summary`
- [x] 1.4 Below-floor guard: skip/flag a finite `--timeout` < task floor unless `--allow-below-floor`; mark such runs non-comparable

## 2. QA / верификация

- [x] 2.1 Test: a long task with `--timeout 2400` resolves to **7200** (floor raises)
- [x] 2.2 Test: `task_432` (`min=max=3600`) with `--timeout 7200` resolves to **3600** (max clamps)
- [x] 2.3 Test: default (no floor) is unchanged
- [x] 2.4 `python3 -m pytest tests/ -q` — targeted test 3 passed; full-suite failures are pre-existing missing-dep (`deepagents`/`langgraph`) and unrelated
- [x] 2.5 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0

## 3. Документация

- [x] 3.1 Effective-timeout rule recorded in ADR-0004 / change design
