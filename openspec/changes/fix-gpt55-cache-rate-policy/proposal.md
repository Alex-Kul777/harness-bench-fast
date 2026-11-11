# Proposal: fix-gpt55-cache-rate-policy

## Why

Cloud.ru биллит gpt-5.5 как `cost = input*854 + output*5124`, где `input` — **полный**
prompt, включая cached prefix (проверено ±0,02% по провайдерской выгрузке). Но каталог
`~/.openclaw/cloudru-prices.json` публикует у `openai/gpt-5.5` `cache_read = 85.4`
(= `input/10`) — это **синтетика**, не совпадающая с фактом.

Политика H2 (спека `price-cache-read-at-input-rate`) покрывает только случай
«публичного cache-тарифа нет» (`cache_read` = 0/None). Здесь тариф **публикуется, но
неверен**, поэтому resolver сохранял 85.4, и стандартный `backfill_cost_rub.py`
**откатывал** корректные ₽ gpt-5.5: 61 966,63 ₽ (cache@input) → ~24 210,80 ₽
(cache@85.4). Публично опубликованные ₽ уже верны и не должны меняться.

## What Changes

1. `harness_bench/cost_resolver.py`: явный механизм override `CACHE_RATE_OVERRIDES`
   «model id → `"input"` | ₽/1M». Для модели с синтетической/неверной публичной
   cache-ставкой cache-read/cache-write тарифицируются по **входной** ставке; resolver
   печатает отличимый NOTE. Применяется и в каталоге, и в config-ветке, и на
   filename-подсказке (через `_finalize_rates`).
2. Правило override — **явная таблица**, а не эвристика «cache == input/10»: публичная
   cache-ставка, равная `input/10`, у части провайдеров легитимна (реальный дисконт),
   поэтому ratio-эвристика опасна и SHALL NOT использоваться.
3. `scripts/backfill_cost_rub.py` — согласован: стандартный бэкфилл даёт ту же цену и
   **не** откатывает gpt-5.5-артефакты назад к 85.4.
4. Тесты `tests/test_cost_gpt55_cache_rate.py` (RED → GREEN).

## Out of scope

- Пересчёт уже опубликованных ₽ gpt-5.5 (они верны; сумма 61 966,63 ₽ сохраняется).
- Реальная cache-ставка DeepSeek-V4.1-Flash (6.5) и прочих моделей — не затрагивается.
- Автодетект «синтетической» ставки по отношению ставок — сознательно исключён.
- Перегенерация `docs/fork-*` и `results/*.json` — не требуется (`--check` == 0).

## Capabilities

### Modified Capabilities
- `benchmark-runs`: override синтетической/неверной публичной cache-ставки → входная
  ставка (gpt-5.5); корректные публичные cache-ставки не затрагиваются.

## Impact

- `harness_bench/cost_resolver.py`
- `tests/test_cost_gpt55_cache_rate.py` (новый)
- `openspec/changes/fix-gpt55-cache-rate-policy/`
- `results/*.json` и `docs/fork-*` — **без изменений** (`build_fork_results/pages/home --check` == 0)

Tracking: Workboard `803a4dc2`; Issue https://github.com/Alex-Kul777/openclaw-workspace/issues/446
