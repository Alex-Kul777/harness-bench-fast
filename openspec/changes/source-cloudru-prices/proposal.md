# Proposal: source-cloudru-prices

## Why

Раннеры форка определяют ₽-ставки только через `~/.openclaw/openclaw.json`, который
может отсутствовать, быть неполным или устареть; при отсутствии модели молча
подставляется fallback. Публичный каталог Cloud.ru Foundation Models
(`GET https://foundation-models.api.cloud.ru/v1/models`, Bearer `$CLOUD_RU_API_KEY`)
уже отдаёт актуальные ставки (`metadata.prompt_tokens_cost`,
`metadata.generated_tokens_cost`, `metadata.cache_read_tokens_cost`) и признак
`metadata.is_billable` — это источник истины (проверено: GigaChat3.5-432B-A28B-Reasoning
= 96.22/288.6 без cache-поля; DeepSeek-V4.1-Flash = 64.94/194.81/6.5).

## What Changes

- Новый скрипт `scripts/sync_cloudru_prices.py`: тянет живой каталог и пишет кэш JSON
  `{fetched_at, models:{"<full model id>":{input,output,cache_read,is_billable}}}` в
  `~/.openclaw/cloudru-prices.json` по умолчанию; флаги `--out` и `--ttl`. При сетевой
  или HTTP-ошибке НЕ перезаписывает прежний кэш и завершается ненулевым кодом.
- `harness_bench/cost_resolver.py`: `resolve_model_rates(model_id)` резолвит ставки в
  порядке (1) запись каталог-кэша → (2) блок `cost` из `~/.openclaw/openclaw.json` →
  (3) явный fallback + WARNING в stderr. Отсутствующее поле `cache_read` считается 0.
  Публичный API (`resolve_model_rates`, `compute_cost_rub`) сохраняется.
- Автотесты `tests/test_cloudru_prices.py`: парсинг каталога (мок httpx), запись/чтение
  кэша + истечение TTL, приоритет cache > config > fallback, значения GigaChat3.5 и
  DeepSeek-V4.1-Flash, fallback-warning для неизвестной модели.
- Change строится на change `fix-runner-cost-rates` (базовый per-model resolver).

Не **BREAKING**: сигнатуры и поведение при отсутствии кэша/конфига совместимы.

## Capabilities

### New Capabilities
- (нет)

### Modified Capabilities
- `benchmark-runs`: требование "Per-model ₽ pricing" расширяется живым каталогом
  Cloud.ru как первичным источником и явным правилом приоритета источников;

ADDED-требование про синхронизацию каталога в той же capability.

## Impact

- Код: `scripts/sync_cloudru_prices.py` (new), `harness_bench/cost_resolver.py`,
  `tests/test_cloudru_prices.py` (new).
- Данные: кэш `~/.openclaw/cloudru-prices.json` (вне репозитория, не коммитится).
- Конфиг `~/.openclaw/openclaw.json` НЕ редактируется (родительский агент отдельно).
- Зависимости: `httpx` (уже используется), stdlib.
- Раннеры (`run_openclaw_bench.py`, `run_pi_bench.py`, `run_hermes_bench.py`) не
  меняются: они уже вызывают resolver.
- Out of scope: pass/fail-методология, схема артефактов, конвертация USD→RUB,
  push/merge, изменение config.

## Ссылки

- Workboard: `ee7af2b7-6e97-4de6-bd3c-d8e783de6791`
- Базируется на change `fix-runner-cost-rates`
