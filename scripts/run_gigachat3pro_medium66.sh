#!/usr/bin/env bash
# Medium-66 benchmark: GigaChat 3 Pro ("GigaChat/GigaChat-3-Pro" on Cloud.ru) on the
# SAME 66 tasks our Pi·DeepSeek Medium coverage used (long 6 + reflect 20 + feasibility 40).
#
# NOTE ON THINKING: GigaChat-3-Pro exposes NO reasoning axis on cloud.ru. The catalog
# entry has no `reasoning: true` (unlike ai-sage/GigaChat3.5-432B-A28B-Reasoning), and a
# direct API probe shows `reasoning_effort` is accepted (HTTP 200) but IGNORED: the
# response's `reasoning` field is empty and no reasoning tokens are produced. So by
# default we run it with NO thinking level (LVL="" -> no --thinking flag), matching the
# single-config pilot. Set LVL=off only if you explicitly want the flag recorded.
#
# Three per-wave invocations (per-wave timeout floors); the artifacts aggregate into a
# Medium row for the fork.
#
# Usage:  bash scripts/run_gigachat3pro_medium66.sh
#         CONC=3 bash scripts/run_gigachat3pro_medium66.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"          # benchmark-research/
RUNNER="$REPO_ROOT/run_pi_bench.py"
RESULTS="$REPO_ROOT/results"
MODEL="${MODEL:-GigaChat/GigaChat-3-Pro}"
LVL="${LVL:-}"                                    # empty = no thinking level (3 Pro has none)
DATE="${DATE:-$(date +%Y%m%d)}"
CONC="${CONC:-3}"

LONG="task_392_manuscript_continuity task_398_card_game_engine task_403_binary_format_reverse task_393_intranet_multihop task_394_review_annotation task_395_homework_grading"
REFLECT="task_413_crm_pagination task_414_batch_partial task_415_api_throttle task_412_supplier_minimum task_416_pay_units task_418_ticket_timeout_dupes task_419_storage_async_delete task_417_transfer_fees task_420_wiki_optimistic_lock task_421_catalog_case_search task_423_rooms_duration_cap task_424_payments_split_limits task_425_shipping_weight_codes task_422_calendar_timezone task_427_report_deprecated_flag task_426_kv_eventual task_429_mail_bounce task_430_orders_backorder task_428_geocode_quota task_431_admin_elevation"
FEAS="task_432_clock_contract task_434_universal_compressor task_435_archive_transfer task_436_search_capabilities task_433_aggregate_identifiability task_437_search_index task_439_ledger_reachability task_440_universal_compressor task_438_opaque_guid task_441_stateless_contract task_443_search_count task_444_stateless_contract task_445_parity_repair task_446_archive_transfer task_447_sealed_partition task_442_ledger_reachability task_449_search_capabilities task_448_aggregate_identifiability task_451_search_index task_450_maintenance_windows task_452_search_hint task_454_search_boundary task_455_maintenance_windows task_453_opaque_guid task_457_search_pool task_458_deployment_matching task_459_replication_cut task_460_replication_cut task_461_search_pool task_462_build_critical_path task_463_diagnostic_queries task_464_search_boundary task_465_search_count task_466_parity_repair task_467_sealed_partition task_468_diagnostic_queries task_469_deployment_matching task_470_search_hint task_471_clock_contract task_456_build_critical_path"

THINK=()
if [[ -n "$LVL" ]]; then THINK=(--thinking "$LVL"); fi

mkdir -p "$RESULTS"
echo "GigaChat 3 Pro${LVL:+ (thinking: $LVL)} — Medium-66 on Pi"
echo "  model: $MODEL | concurrency: $CONC | waves: long(6)/reflect(20)/feasibility(40)"

run_wave() {
  local wave="$1" tmo="$2"; shift 2
  local out="$RESULTS/pi_medium_${wave}_gigachat3pro_${DATE}.json"
  echo ">>> [$wave] timeout=${tmo}s -> $out"
  PYTHONUNBUFFERED=1 python3 -u "$RUNNER" --tasks "$@" \
      --model "$MODEL" "${THINK[@]}" --timeout "$tmo" --concurrency "$CONC" \
      --json-output "$out" --status-file "/tmp/pi_gigachat3pro_medium_${wave}_status.json" \
      2>&1 | tee "/tmp/pi_gigachat3pro_medium_${wave}.log"
}

# shellcheck disable=SC2086
run_wave long        7200 $LONG
# shellcheck disable=SC2086
run_wave reflect     1800 $REFLECT
# shellcheck disable=SC2086
run_wave feasibility 3600 $FEAS
echo "Done. Medium-66 artifacts: $RESULTS/pi_medium_{long,reflect,feasibility}_gigachat3pro_${DATE}.json"
