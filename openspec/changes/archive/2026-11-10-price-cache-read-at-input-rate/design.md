# Design: price-cache-read-at-input-rate

## ADR-inline — cache-тариф отсутствует → входная ставка (H2)

**Решение (owner-confirmed).** Когда у определённой модели нет публичного
cache-тарифа (`cacheRead`/`cacheWrite` отсутствует, `None` или `0`), cache-read и
cache-write токены тарифицируются по **входной** ставке этой же модели. Публичная
cache-ставка сохраняется как есть (например DeepSeek-V4.1-Flash `cacheRead` = 6.5).
Политика применяется в `harness_bench.cost_resolver.compute_cost_rub`
(`cache_rate_or_input`), поэтому её видят и раннер, и бэкфилл.

**Обоснование (billing cross-check).** MiniMax-M3 all-users spend за 2 дня = 58.00k ₽;
наши MiniMax-артефакты = 140.06M токенов. cache@0 → 9.66k ₽ (слишком мало),
cache@output → 124.37k ₽ (> 58k, невозможно), cache@input → 36.97k ₽ (согласуется).
Единственная согласованная ставка — входная, поэтому публикуемый `cache_read = 0.0`
трактуется как «нет cache-тарифа», а не как «бесплатный cache».

**Notes (различение).** `resolve_model_rates` печатает
`[cost_resolver] NOTE: no published cache tariff for '<model>'; cache tokens priced at
the INPUT rate (N ₽/1M).` для моделей без cache-тарифа и молчит, когда cache-ставка
публичная. Громкий `WARNING` для неопределимой модели сохранён.

## Assumption — откуда берётся cache-бакет

OpenClaw-конверт usage = `{input, output, total, reasoningTokens}` — **без явного
cache-поля**. Поэтому cache-бакет выводится один раз как
`cache_read = max(total_tokens - input - output, 0)` (при `total_tokens = input +
output + cache_read + cache_write`) и **сохраняется явно** (per-task и в summary),
чтобы читатели больше не выводили его на чтении. Если у провайдера появится реальное
cache-поле — предпочитать его (в раннере `has_explicit_cache`, в бэкфилле
`has_explicit_cache`), не переопределяя из `total_tokens`.

## Изменения

- `cost_resolver.compute_cost_rub`: cache-токены по `cache_read`/`cache_write`, если
  ставка > 0, иначе по `input`.
- `run_openclaw_bench._write_results`: явные `summary.total_cache_read_tokens` /
  `total_cache_write_tokens`; вывод per-task при отсутствии.
- `scripts/backfill_cost_rub.py`: PREFER явные бакеты, иначе вывод; запись обратно.

## Тесты

- `tests/test_cost_cache_input_rate_policy.py` (новый): None-cache модель тарифицирует
  cache-бакет по входной ставке; публичная ставка сохраняется; resolver печатает NOTE;
  раннер/бэкфилл пишут `total_cache_read_tokens`. Red до фикса, green после.
- `tests/test_cost_cache_bucket.py`, `tests/test_cost_filename_hints.py` — остаются
  зелёными.

## Свидетельства

- `oc_medium_feasibility_minimaxm3_off_20261109.json`: 1234.93 → **8635.58 ₽**.
- `pi_shotlist_gigachat3pro.json`: 62.12 → **956.96 ₽**.
- `oc_medium_feasibility_ds41flash_off_20261108.json`: **572.89 ₽** (без изменений,
  публичная cache-ставка 6.5).
