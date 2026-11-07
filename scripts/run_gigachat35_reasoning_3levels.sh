#!/usr/bin/env bash
# Benchmark kit: GigaChat 3.5 Reasoning on the Pi harness, 3 reasoning levels.
#
# Model : ai-sage/GigaChat3.5-432B-A28B-Reasoning  (Cloud.ru, reasoning: true)
# Levels: low / medium / high  (mapped to reasoning_effort via Pi --thinking)
# Suite : 52-task shot list (default) — override with SUITE_ARGS.
#
# Each level runs as its own supervised, unbuffered invocation so a completion
# wakes the session; JSON + status go to the shared results dir the fork sync reads.
#
# Usage:
#   bash scripts/run_gigachat35_reasoning_3levels.sh
#   LEVELS="low high" CONCURRENCY=3 bash scripts/run_gigachat35_reasoning_3levels.sh
#   SUITE_ARGS="--pilot" bash scripts/run_gigachat35_reasoning_3levels.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"          # benchmark-research/
RUNNER="$REPO_ROOT/run_pi_bench.py"
RESULTS_DIR="$REPO_ROOT/results"

MODEL="${MODEL:-ai-sage/GigaChat3.5-432B-A28B-Reasoning}"
DATE="${DATE:-$(date +%Y%m%d)}"
CONCURRENCY="${CONCURRENCY:-2}"
# shellcheck disable=SC2206
LEVELS=(${LEVELS:-low medium high})
# shellcheck disable=SC2206
SUITE_ARGS=(${SUITE_ARGS:---shot-list})

mkdir -p "$RESULTS_DIR"
echo "GigaChat 3.5 Reasoning — 3 levels on Pi"
echo "  model: $MODEL | levels: ${LEVELS[*]} | concurrency: $CONCURRENCY | suite: ${SUITE_ARGS[*]}"

for LVL in "${LEVELS[@]}"; do
  OUT="$RESULTS_DIR/pi_shotlist_giga35_reasoning_${LVL}_${DATE}.json"
  LOG="/tmp/pi_giga35_reasoning_${LVL}.log"
  STATUS="/tmp/pi_giga35_${LVL}_status.json"
  echo ">>> [$LVL] -> $OUT  (log: $LOG)"
  PYTHONUNBUFFERED=1 python3 -u "$RUNNER" \
      "${SUITE_ARGS[@]}" --model "$MODEL" --thinking "$LVL" \
      --concurrency "$CONCURRENCY" \
      --json-output "$OUT" --status-file "$STATUS" 2>&1 | tee "$LOG"
done
echo "Done. Artifacts in $RESULTS_DIR (pi_shotlist_giga35_reasoning_*_${DATE}.json)"
