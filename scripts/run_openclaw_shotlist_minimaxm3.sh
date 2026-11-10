#!/usr/bin/env bash
# Shot List (52 tasks) on the OpenClaw harness — MiniMaxAI/MiniMax-M3.
# Levels default: off medium ultra  (Cloud.ru API 'none'==harness 'off'; MiniMax-M3 top tier is 'ultra', NOT 'max').
# 52-task stratified sample -> harness-bench-fast/shot_list.txt.
#
# Usage:  bash scripts/run_openclaw_shotlist_minimaxm3.sh
#         LEVELS="off medium max" CONC=3 bash scripts/run_openclaw_shotlist_minimaxm3.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"       # HBF/scripts
REPO_ROOT="$(cd "$HERE/.." && pwd)"         # HBF root (runners co-located here)
RUNNER="$REPO_ROOT/run_openclaw_bench.py"
RESULTS="$REPO_ROOT/results"
MODEL="${MODEL:-custom-foundation-models-api-cloud-ru/MiniMaxAI/MiniMax-M3}"
LEVELS="${LEVELS:-off medium ultra}"
DATE="${DATE:-$(date +%Y%m%d)}"
CONC="${CONC:-3}"
TMO="${TMO:-7200}"

mkdir -p "$RESULTS"
echo "== OpenClaw — MiniMax-M3 — Shot List (52) =="
echo "   model: $MODEL | levels: $LEVELS | concurrency: $CONC | timeout: $TMO"

for LVL in $LEVELS; do
  out="$RESULTS/oc_shotlist_minimaxm3_${LVL}_${DATE}.json"
  echo ">>> [shotlist/$LVL] timeout=${TMO}s -> $out"
  PYTHONUNBUFFERED=1 python3 -u "$RUNNER" --shot-list \
      --model "$MODEL" --thinking "$LVL" --timeout "$TMO" --concurrency "$CONC" \
      --json-output "$out" --status-file "/tmp/oc_shotlist_minimaxm3_${LVL}_status.json" \
      2>&1 | tee "/tmp/oc_shotlist_minimaxm3_${LVL}.log"
done
echo "Done. -> $RESULTS/oc_shotlist_minimaxm3_<lvl>_${DATE}.json"
