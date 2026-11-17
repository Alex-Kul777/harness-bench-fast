#!/usr/bin/env bash
# Minimal repro: OC runner crashes on long/hard task with EventEmitter listener leak.
#
# Symptom: exit=1, 0 tokens; stderr contains
#   "MaxListenersExceededWarning: ... 11 connect listeners added to [Socket]"
#   and either "Provider returned an incomplete or malformed tool call"
#   or "403 Input text May contain sensitive information, please try again."
#
# Reproduced 2/2 on 2026-11-16. Card: <workboard>. Doc:
#   docs/research/2026-11-17-openclaw-exec-crash-diagnosis.md
set -u
cd "$(dirname "$0")/.."

MODEL="custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash"
TASK="${1:-task_403_binary_format_reverse}"
TIMEOUT="${2:-7200}"

echo "[repro] running OC arm on $TASK (timeout=${TIMEOUT}s); expect exit=1 + 0 tokens"
python3 -u run_openclaw_bench.py \
  --tasks "$TASK" --thinking off \
  --model "$MODEL" --timeout "$TIMEOUT" \
  --json-output "results/repro_oc_${TASK}_$(date +%Y%m%d).json" \
  --status-file "/tmp/repro_oc_status.json"

echo "[repro] check the JSON: total_tokens should be 0 and passed=false"
