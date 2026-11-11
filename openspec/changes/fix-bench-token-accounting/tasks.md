# Tasks: fix-bench-token-accounting

## Диагностика
- [x] Прочитать `run_pi_bench.py`, `run_openclaw_bench.py`, `harness_bench/cost_resolver.py`, `scripts/backfill_cost_rub.py`
- [x] Подтвердить ×3 по сырому NDJSON (ratio out 3.05 / in 3.02; `message_end`+`turn_end`+`agent_end`)
- [x] Подтвердить инвариант Pi: `total = input + output + cacheRead + cacheWrite`
- [x] Probe OpenClaw: конверт даёт явные `cacheRead`/`cacheWrite`/`reasoningTokens`; `total = input+output+cacheRead+cacheWrite`
- [x] Проверить биллинг-модель: `cost = in*854 + out*5124` (±0,02%); cached input биллится по входной ставке
- [x] Установить billing-аккаунты: Pi → `oait`, OpenClaw → `kap-openclaw`

## Реализация
- [x] `run_pi_bench._extract_usage`: single-source учёт (дедуп по `responseId`), cache-бакеты
- [x] `run_pi_bench`: per-task `agent_cache_read_tokens`/`agent_cache_write_tokens`; summary cache/reasoning; ₽ с cache
- [x] `run_openclaw_bench.run_one_task`: чтение явных `usage.cacheRead`/`usage.cacheWrite`
- [x] `run_openclaw_bench._write_results`: явные бакеты + fallback из инварианта; `total_reasoning_tokens`
- [x] `scripts/backfill_token_buckets.py`: пересчёт бакетов/₽ 10 gpt-5.5 артефактов

## Данные
- [x] Backfill `results/*gpt55*20261110.json` (10 файлов) → сумм. 61 966,63 ₽
- [x] Fixture `tests/fixtures/gpt55_provider_slice.csv` (обрезанный срез: `kap-openclaw` + `oait`)
- [x] Перегенерировать `docs/fork-*` (`build_fork_results`, `build_fork_pages`, `build_fork_home`)

## QA
- [x] RED→GREEN: `tests/test_cost_gpt55_reconciliation.py` (5 passed), `tests/test_runner_pi_cleanup.py`
- [x] `python3 -m pytest tests/test_cost_*.py tests/test_runner_pi_cleanup.py -q` → 25 passed
- [x] `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [x] `python3 scripts/build_fork_results.py --check` / `--lint` → 0
- [x] `python3 scripts/build_fork_pages.py --check` → 0; `python3 scripts/build_fork_home.py --check` → 0
- [x] Сверка: Pi-волна vs `oait` = **−0,52%** (±1%); суммарно vs `oait+kap-openclaw` = **−9,5%** (не сошлось — см. design.md)
