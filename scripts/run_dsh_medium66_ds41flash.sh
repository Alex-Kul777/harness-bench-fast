#!/usr/bin/env bash
# Medium-66 benchmark on the DeepSeek Harness (dsh) — DeepSeek-V4.1-Flash
# (thinking: off | medium | high). SAME 66 tasks as our Pi·DeepSeek / OpenClaw·DeepSeek
# Medium coverage (long 6 + reflect 20 + feasibility 40), so rows are directly comparable.
# Per-wave timeout floors (7200/1800/3600) -> one invocation per wave per level.
# FORK-OWNED (HBF benchmark script).
# Usage:  bash scripts/run_dsh_medium66_ds41flash.sh
#         LEVELS="off medium high" CONC=3 bash scripts/run_dsh_medium66_ds41flash.sh
#         PILOT=1 bash scripts/run_dsh_medium66_ds41flash.sh   # 2 tasks/wave, /tmp outputs
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"       # HBF/scripts
REPO_ROOT="$(cd "$HERE/.." && pwd)"         # HBF root (runners co-located here)
RUNNER="$REPO_ROOT/run_dsh_bench.py"
RESULTS="$REPO_ROOT/results"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4.1-Flash}"
LEVELS="${LEVELS:-off}"
WAVES="${WAVES:-long reflect feasibility}"
DATE="${DATE:-$(date +%Y%m%d)}"
CONC="${CONC:-3}"
PILOT="${PILOT:-0}"

LONG="task_392_manuscript_continuity task_398_card_game_engine task_403_binary_format_reverse task_393_intranet_multihop task_394_review_annotation task_395_homework_grading"
REFLECT="task_413_crm_pagination task_414_batch_partial task_415_api_throttle task_412_supplier_minimum task_416_pay_units task_418_ticket_timeout_dupes task_419_storage_async_delete task_417_transfer_fees task_420_wiki_optimistic_lock task_421_catalog_case_search task_423_rooms_duration_cap task_424_payments_split_limits task_425_shipping_weight_codes task_422_calendar_timezone task_427_report_deprecated_flag task_426_kv_eventual task_429_mail_bounce task_430_orders_backorder task_428_geocode_quota task_431_admin_elevation"
FEAS="task_432_clock_contract task_434_universal_compressor task_435_archive_transfer task_436_search_capabilities task_433_aggregate_identifiability task_437_search_index task_439_ledger_reachability task_440_universal_compressor task_438_opaque_guid task_441_stateless_contract task_443_search_count task_444_stateless_contract task_445_parity_repair task_446_archive_transfer task_447_sealed_partition task_442_ledger_reachability task_449_search_capabilities task_448_aggregate_identifiability task_451_search_index task_450_maintenance_windows task_452_search_hint task_454_search_boundary task_455_maintenance_windows task_453_opaque_guid task_457_search_pool task_458_deployment_matching task_459_replication_cut task_460_replication_cut task_461_search_pool task_462_build_critical_path task_463_diagnostic_queries task_464_search_boundary task_465_search_count task_466_parity_repair task_467_sealed_partition task_468_diagnostic_queries task_469_deployment_matching task_470_search_hint task_471_clock_contract task_456_build_critical_path"

if [ "$PILOT" = "1" ]; then
  LONG="task_392_manuscript_continuity task_394_review_annotation"
  REFLECT="task_413_crm_pagination task_414_batch_partial"
  FEAS="task_432_clock_contract task_439_ledger_reachability"
  OUTDIR="${OUTDIR:-/tmp}"
else
  OUTDIR="$RESULTS"
fi

mkdir -p "$( [ "$PILOT" = 1 ] && echo "$OUTDIR" || echo "$RESULTS" )"
echo "== DeepSeek Harness (dsh) — DeepSeek-V4.1-Flash — Medium-66${PILOT:+ (PILOT=$PILOT)} =="
echo "   model: $MODEL | runner: $RUNNER"
echo "   levels: $LEVELS | concurrency: $CONC | waves: long(6)/reflect(20)/feasibility(40)"

run_wave() {
  local lvl="$1" wave="$2" tmo="$3"; shift 3
  local out="$OUTDIR/dsh_medium_${wave}_ds41flash_${lvl}_${DATE}.json"
  echo ">>> [$lvl/$wave] timeout=${tmo}s -> $out"
  PYTHONUNBUFFERED=1 python3 -u "$RUNNER" --tasks "$@" \
      --model "$MODEL" --thinking "$lvl" --timeout "$tmo" --concurrency "$CONC" \
      --permission-mode workspace-write \
      --json-output "$out" --status-file "/tmp/dsh_medium_${wave}_${lvl}_status.json" \
      2>&1 | tee "/tmp/dsh_medium_${wave}_${lvl}.log"
}

for LVL in $LEVELS; do
  case " $WAVES " in *" long "*)        run_wave "$LVL" long        7200 $LONG ;; esac
  case " $WAVES " in *" reflect "*)     run_wave "$LVL" reflect     1800 $REFLECT ;; esac
  case " $WAVES " in *" feasibility "*) run_wave "$LVL" feasibility 3600 $FEAS ;; esac
done
echo "Done. Artifacts -> $OUTDIR/dsh_medium_{long,reflect,feasibility}_ds41flash_<lvl>_${DATE}.json"
