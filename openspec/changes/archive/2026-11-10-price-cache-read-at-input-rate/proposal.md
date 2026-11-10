# Proposal: price-cache-read-at-input-rate

## Why

`summary.estimated_cost_rub` занижена для моделей **без публичного cache-тарифа**:
MiniMax-M3 и GigaChat-3-Pro публикуют `cache_read = 0.0`, поэтому cache-read бакет
(основной объём prompt-токенов на длинных прогонах) тарифицировался как 0.

Кросс-проверка по биллингу (owner-confirmed): за 2 дня all-users spend MiniMax-M3 =
**58.00k ₽**, наши MiniMax-артефакты = **140.06M токенов**:

| cache-ставка | расчёт | вывод |
|---|---|---|
| cache@0 | 9.66k ₽ | слишком мало |
| cache@output | 124.37k ₽ | > 58k ₽, невозможно |
| cache@input | 36.97k ₽ | согласуется |

Значит правильная политика — **cache-бакет по входной ставке**, когда публичного
cache-тарифа нет. Публичный cache-тариф (DeepSeek-V4.1-Flash = 6.5) сохраняется.

## What Changes

1. `harness_bench/cost_resolver.py`: при отсутствии/None публичного cache-тарифа
   (`cacheRead`/`cacheWrite`) `compute_cost_rub` тарифицирует cache-токены по **входной
   ставке** модели; публичная cache-ставка сохраняется. `resolve_model_rates` выводит
   явный NOTE, различающий «публичная cache-ставка» и «нет cache-тарифа → входная ставка».
2. `run_openclaw_bench.py::_write_results`: **явные** cache-бакеты
   `summary.total_cache_read_tokens` / `total_cache_write_tokens`; источник — per-task
   `agent_cache_read_tokens`/`agent_cache_write_tokens`, иначе вывод
   `cache_read = max(total_tokens - input - output, 0)` на этапе записи (и сохранение
   выведенного значения per-task).
3. `scripts/backfill_cost_rub.py`: PREFER `summary.total_cache_read_tokens`, иначе вывод
   `total_tokens - input - output`; запись явных бакетов обратно; цена — через resolver.
4. Тесты (red → green) + backfill `results/` + перегенерация форк-страниц.

## Capabilities

### Modified Capabilities
- `benchmark-runs`: явные cache-бакеты в артефакте; тариф cache-бакета по входной ставке
  при отсутствии публичного cache-тарифа.

## Impact

- `harness_bench/cost_resolver.py`, `run_openclaw_bench.py`, `scripts/backfill_cost_rub.py`
- `tests/test_cost_cache_input_rate_policy.py` (новый), смежные cost-тесты
- `results/*.json` (явные cache-бакеты + пересчитанная `estimated_cost_rub`)
- `docs/fork-*` (перегенерация таблиц)
