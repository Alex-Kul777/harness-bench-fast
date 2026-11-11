# Tasks: fix-gpt55-cache-rate-policy

## Диагностика
- [x] Подтвердить факт-биллинг gpt-5.5: `cost = input*854 + output*5124`, input = полный prompt (±0,02%)
- [x] Подтвердить, что каталог публикует `cache_read = 85.4` (= input/10) — синтетика
- [x] Подтвердить регрессию: стандартный `backfill_cost_rub.py` откатывает gpt-5.5 к 85.4

## Реализация
- [x] `harness_bench/cost_resolver.py`: `CACHE_RATE_OVERRIDES` + `resolve_cache_rate_override` + `_apply_cache_rate_override` + `_finalize_rates`
- [x] Подключить override во всех ветках разрешения ставок (каталог / config / filename-подсказка)
- [x] Явный NOTE при срабатывании override; DeepSeek (6.5) не затронут
- [x] Тесты `tests/test_cost_gpt55_cache_rate.py` (RED → GREEN)

## Данные
- [x] Проверить, что `results/*gpt55*20261110.json` НЕ меняются; сумма = 61 966,63 ₽
- [x] `backfill_cost_rub.py results --dry-run` → `0 updated`

## QA / Verification
- [x] `python3 -m pytest tests/test_cost_*.py -q` — зелёный
- [x] `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
- [x] `python3 scripts/build_fork_results.py --check` == 0
- [x] Свидетельства: gpt-5.5 cache 85.4 → 854.0; сумма до/после = 61 966,63 ₽
