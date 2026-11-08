# Proposal: fix-runner-cost-rates

## Проблема

Раннеры `run_openclaw_bench.py`, `run_pi_bench.py`, `run_hermes_bench.py` хардкодят
константы стоимости GLM-5.2 (239.12 / 751.52 ₽/1M) и применяют их ко **всем** моделям.
Cache-read токены не тарифицируются вовсе. Аудит (subagent 4fe4b789) показал: для
2-строчного прогона DeepSeek-V4.1-Flash итоговая стоимость завышена в 2.83× (569.49 ₽
против корректных 201.62 ₽, при этом 49.25 ₽ cache-read потеряно).

## Решение

Ввести per-model resolver стоимости: читает `~/.openclaw/openclaw.json` (или путь из
переменной окружения `OPENCLAW_CONFIG`), извлекает блок `cost` для нужной модели
(input / output / cacheRead / cacheWrite ₽ за 1M), применяет ко всем трём раннерам.

## Что входит в scope

- Resolver `harness_bench/cost_resolver.py`
- Патч трёх раннеров (только ₽-аккаунтинг, pass/fail не трогается)
- Тесты `tests/test_runner_cost_*.py`
- Скрипт `scripts/backfill_cost_rub.py` (пересчёт committed артефактов)
- OpenSpec MODIFIED-блок для `benchmark-runs` и `result-reporting`

## Что НЕ входит в scope

- Изменение методологии pass/fail верификации
- Добавление новых полей в JSON-схему артефактов, кроме уже существующих
- Push / merge в main

## Ссылки

- Workboard: `ee7af2b7-6e97-4de6-bd3c-d8e783de6791`
- Проблема подтверждена аудитом subagent `4fe4b789`
