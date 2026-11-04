---
name: harness-bench-fast
description: Work with the harness-bench-fast benchmark repo (projects/benchmark-research): run shot-list and new waves (long-context 392–411, tool-reflection 412–431, feasibility/wave19 432–471), onboard Cloud.ru models, fix the Pi/OpenClaw runners, merge upstream. Use whenever benchmarking models on this repo.
---

# harness-bench-fast — Benchmark Workflow

Procedure for scoring models on the `harness-bench-fast` benchmark and keeping the
runners healthy. Repo root: `~/.openclaw/workspace/projects/benchmark-research`
(checkout in `harness-bench-fast/`).

## When to use
Any work touching this repo: running a model on the shot list or a new wave,
onboarding a Cloud.ru model, diagnosing/fixing a runner, merging upstream, or
publishing results. Load this skill before the run.

## Repo map
- `run_pi_bench.py` — Pi Agent harness runner (default first wave; fastest/cheapest).
- `run_openclaw_bench.py` — OpenClaw harness runner (second wave; `--model` uses the
  full provider-prefixed id).
- `harness-bench-fast/shot_list.txt` — the 52-task stratified sample (Light, 391 set).
- `harness-bench-fast/harness_bench/{long,reflect,feasibility}_tasks/` — new waves.
- `results/` — per-run JSON envelopes; commit key ones under `runs/` in the checkout.
- `tests/test_runner_pi_cleanup.py` — runner regression suite.
- `docs/SPEC-new-waves-track.md`, repo `AGENTS.md`.

## Environment prerequisites
- `CLOUD_RU_API_KEY` in env (or the Hermes `.env`). Never print its value.
- Docker image `pi-sandbox:latest` must exist and **contain `python3`** (wave19's
  `taskctl` is Python). Rebuild: `docker build -t pi-sandbox:latest -f ~/pi-agent/Dockerfile.pi ~/pi-agent`.
- Add every new model to `~/.openclaw/openclaw.json` under the Cloud.ru provider id
  `custom-foundation-models-api-cloud-ru/<catalog-id>` in TWO places (models block + `modelPolicy.allow`).
  Never add the bare catalog id (`z-ai/…`, `zai/…`) — it resolves to the direct z.ai provider and fails.

## Run a model (two waves)
1. List the catalog: `python3 scripts/fm.py models` (skill `cloudru-foundation-models`);
   verify access with `python3 scripts/fm.py call "<id>" --prompt "Reply with exactly: OK"`.
   `403` on a whole namespace = key lacks it (ask user); `404` = wrong id.
2. Pilot: `python3 run_pi_bench.py --pilot --model '<catalog-id>' --concurrency 2 --json-output results/pi_pilot_<name>.json`.
   Go/no-go: ≥7/12 PASS and no systematic API errors.
3. Full shot list, Pi first, then OpenClaw — the user wants a model × harness table.
4. Run on the benchmark commit currently checked out; do **not** merge upstream first or scores become incomparable.

## Run a new upstream wave (task-set v0.21.3+)
1. Confirm the runner loads the wave's ids:
   `python3 -c "import sys;sys.path.insert(0,'.');from harness_bench.tasks import get_task;assert callable(get_task('<id>').verify)"`.
2. Pass `--timeout` per wave: ordinary/reflection 1800s, wave19 3600s, long-context 7200s.
   `--timeout` is one value → run each wave as its own invocation.
3. Smoke-test one task per wave before the full set (wiring signal = verifier ran, not the task's PASS).
4. Sample a wave before its full set; incumbent best model first, others after.
5. Launch long waves as a supervised background process (`PYTHONUNBUFFERED=1 python3 -u …` +
   `--status-file`) so completion wakes the session. Unbuffered output is required or progress stalls.
6. To let the user watch live, launch in their Control UI terminal: `terminal list`, then
   `terminal input` the exact unbuffered command with a trailing newline, then `terminal read` and
   confirm the banner is visible. Detached `tmux` does **not** survive here — never rely on it.

## Runner health (facts learned the hard way)
- The Pi runner names its container `pi-bench-<task>-<ts>` and `docker kill`/`rm -f`s it on timeout
  → no orphan. If `docker ps` shows a `pi-bench-*`, stop it.
- It streams agent output to `/tmp/pi_bench_out_<task>_<ts>.ndjson`; partial usage survives a kill.
  Count API turns from `message_end`/`agent_end`, skip `message_update` deltas, or steps inflate to thousands.
- **wave19 service**: a `task service unavailable: [Errno 2]` from `taskctl submit` means the runner,
  not the model, is at fault. Fix both: (a) mount the host socket dir at the same absolute path
  (`-v <sock_dir>:<sock_dir>`, from `<workspace>/.svc/connection.json`); (b) install `python3` in the image.
  Re-run and require `submission_count >= 1`.
- After editing the Pi runner: `python3 -m pytest tests/test_runner_pi_cleanup.py -q` — require green.

## Run in subagents
One subagent per model run: exact command, cwd, `/tmp` progress log, "do not commit/push",
3-errors → `ESCALATE_TO_SENIOR`. Rerun only failed tasks (`--tasks … --fresh` / `--rerun-on-fail`).

## Resume interrupted runs
Gateway restarts interrupt runs; partial JSON survives.
- Pi runner: rows under `results` (flag `passed`); OpenClaw runner: rows under `tasks`, summary at top
  level — handle both schemas.
- Remaining = shot list minus done ids; run to `*_part2.json`, then merge (concatenate + recompute summary).

## Definition of done
- Runner tests green; no orphan containers.
- Results in `results/*.json` (and committed `runs/*.json` when published).
- README shot-list table row added with the run's Date, harness, model, result, tokens, cost.
- `progress_card` / dashboard report updated.
