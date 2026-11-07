# GigaChat 3.5 Reasoning — 3 reasoning levels on Pi (prepared benchmark)

## QoI
Compare **GigaChat 3.5 Reasoning** (`ai-sage/GigaChat3.5-432B-A28B-Reasoning`, Cloud.ru)
on the Pi harness at **three reasoning levels** — `low` / `medium` / `high` — to measure how
reasoning depth trades off against pass rate, tokens and cost.

## Wiring (verified)
- **API:** `https://foundation-models.api.cloud.ru/v1` accepts `reasoning_effort`
  (`low|medium|high`); responses carry `reasoning_content`. Reachability + a plain call = OK.
- **Pi:** thinking levels map to `reasoning_effort` via the model's `thinkingLevelMap`,
  with `compat.thinkingFormat="openai"` pinned (no URL auto-detect ambiguity).
- **Registration:** added to `~/pi-agent/models.json` under provider `cloud-ru`
  (`reasoning: true`, `maxTokens: 32768`, level map, openai compat). Backup written alongside.
- **Levels differ** (single-turn probe, thinking chars): low ≈ 9.3k · medium ≈ 32.8k · high ≈ 45.5k.
  High exhausted the 16k output cap → `maxTokens` raised to **32768** (API accepts it).

## Run
```bash
cd ~/.openclaw/workspace/projects/benchmark-research
bash harness-bench-fast/scripts/run_gigachat35_reasoning_3levels.sh
# levels / concurrency / suite overridable:
LEVELS="low high" CONCURRENCY=3 SUITE_ARGS="--pilot" \
  bash harness-bench-fast/scripts/run_gigachat35_reasoning_3levels.sh
```
Sequential, unbuffered, per-level status file + log (`/tmp/pi_giga35_<lvl>.log`).
Long runs: launch under `exec timeoutSeconds=0` (or a Control UI terminal) — a full shot list
per level can exceed the ~30 min exec lifetime.

## Cost estimate
Price constants in `run_pi_bench.py`: 239.12 ₽/M input, 751.52 ₽/M output.
At three levels the depth scales, so output tokens (not pass rate) dominate cost.
Estimate is filled in per level once the low run lands (anchor), then ×~1.5–2 for medium, ×~2.5–3 for high.

## Artifacts
- `results/pi_shotlist_giga35_reasoning_{low,medium,high}_<date>.json`
- On success + `--check`/`openspec validate` green → 3 rows in the fork table (Pi · GigaChat 3.5 Reasoning · low/medium/high).

## Risks
- **Truncation at high:** reasoning shares the output budget; long tasks may hit the cap. Watch `finish_reason`.
- **Cost is 0 in models.json** (Cloud.ru catalog price unknown) → the runner's ₽ figure is an estimate.
- **Comparability:** run on the currently checked-out benchmark commit; do not merge upstream first.
