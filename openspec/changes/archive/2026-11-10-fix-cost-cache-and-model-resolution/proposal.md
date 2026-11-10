# Proposal: fix-cost-cache-and-model-resolution

## Проблема

`summary.estimated_cost_rub` в части `results/*.json` занижена по двум причинам:

1. **Потерянный cache-read бакет.** `run_openclaw_bench.py::_write_results` суммирует
   `agent_cache_read_tokens` — ключ, которого в per-task записях нет, поэтому
   cache-read тарифицируется как 0. Та же дыра в `scripts/backfill_cost_rub.py`
   (читает отсутствующий `total_cache_read_tokens`). cache-read — основной объём
   prompt-токенов на длинных прогонах, поэтому стоимость сильно занижена.
2. **Слепой fallback GLM-5.2.** Артефакты без полей `model`/`command`
   (`pi_shotlist_gigachat3pro.json`, `pi_*gigachat3pro_20261109.json`) молча
   оцениваются по ставкам GLM-5.2, хотя семейство однозначно читается из имени файла.

Подтверждено аудитом: `oc_medium_feasibility_ds41flash_off_20261108.json` должен стоить
572.89 ₽ вместо 406.76 ₽; `pi_shotlist_gigachat3pro.json` — 62.12 ₽ вместо 230.44 ₽.

## Решение

1. `harness_bench/cost_resolver.py`: карта подсказок «имя файла → канонический id»
   (`gigachat3pro`, `giga35`, `glm52`, `glm53`, `qwen36`, `oss120b`, `minimaxm3`,
   `ds41flash`), применяемая в `resolve_model_rates(model_id, filename=None)` как
   последнее средство перед fallback GLM-5.2; громкое предупреждение сохраняется.
2. `scripts/backfill_cost_rub.py`: передавать имя артефакта в resolver; восстанавливать
   `cache_read = total_tokens - input - output`, когда явного cache-поля нет.
3. `run_openclaw_bench.py::_write_results`: восстанавливать cache-read бакет из
   `total_tokens`, когда явных cache-полей нет.
4. Тесты: `tests/test_cost_cache_bucket.py`, `tests/test_cost_filename_hints.py`.
5. Backfill committed артефактов + перегенерация форк-страниц.

## Что входит в scope

- Resolver и его карта подсказок; cache-read derivation в раннере и бэкфилле
- Два регрессионных теста (cache-бакет, подсказки имени файла)
- Backfill `results/` и перегенерация `docs/fork-*`
- OpenSpec MODIFIED/ADDED для `benchmark-runs`

## Что НЕ входит в scope

- Изменение методологии pass/fail и формулы ставок
- Ручная правка ставок (ставки берутся из `~/.openclaw/cloudru-prices.json` / config)
- Изменение upstream-методологии в `README.md`

## Ссылки

- Workboard: `ede13b78-1b03-44eb-a7f4-0b5cb641e7d9`
- Предыдущий cost-фикс: `openspec/changes/archive/…-fix-runner-cost-rates`
