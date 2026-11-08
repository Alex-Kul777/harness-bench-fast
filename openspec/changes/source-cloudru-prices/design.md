# Design: source-cloudru-prices

## ADR-inline

**Решение:** ставки ₽ резолвятся из живого каталога Cloud.ru Foundation Models через
локальный кэш-файл; конфиг `openclaw.json` становится вторичным источником.

Этот change строится на `fix-runner-cost-rates` (базовый per-model resolver
`harness_bench/cost_resolver.py`, перенос раннеров на него).

### Источник истины

`GET https://foundation-models.api.cloud.ru/v1/models` (Bearer `$CLOUD_RU_API_KEY`)
→ `data[].metadata.{prompt_tokens_cost, generated_tokens_cost,
cache_read_tokens_cost, is_billable}`.

Проверенные значения (2026-11-08):
- `ai-sage/GigaChat3.5-432B-A28B-Reasoning`: input 96.22 / output 288.6 / нет cache-поля
- `deepseek-ai/DeepSeek-V4.1-Flash`: input 64.94 / output 194.81 / cache_read 6.5

### Формат кэша

`~/.openclaw/cloudru-prices.json`:

```json
{
  "fetched_at": "<ISO8601 UTC>",
  "models": {
    "<full model id>": {"input": 0.0, "output": 0.0, "cache_read": 0.0, "is_billable": true}
  }
}
```

### Скрипт синхронизации `scripts/sync_cloudru_prices.py`

- `--out` (default `~/.openclaw/cloudru-prices.json`), `--ttl` (default 24h),
  `--force`, `--url`, `--timeout`.
- TTL: свежий кэш (`fetched_at` в пределах `--ttl`) → выход 0 без обращения к сети.
- Атомарная запись: temp-файл в том же каталоге + `os.replace`.
- Сеть/HTTP-ошибка или пустой каталог → прежний файл НЕ трогается, exit 1
  (не клобберим хороший кэш).

### Resolver precedence

`resolve_model_rates(model_id, config_path=None, cache_path=None)`:

1. каталог-кэш (`$CLOUDRU_PRICES_CACHE` → `~/.openclaw/cloudru-prices.json`);
   совпадение по полному id или по суффиксу (model_id заканчивается на `/<key>`);
   отсутствующий `cache_read` → 0; `cacheWrite` = 0.
2. блок `cost` из `openclaw.json` (существующая логика `fix-runner-cost-rates`).
3. fallback GLM-5.2 (239.12/751.52/0/0) + WARNING в stderr.

Публичный API сохранён: `resolve_model_rates`, `compute_cost_rub`
(ключи словаря `input` / `output` / `cacheRead` / `cacheWrite`).

### Почему кэш, а не прямой сетевой запрос из раннера

Раннеры вызывают resolver по нескольку раз на задачу; сетевой запрос на каждый вызов
добавил бы задержку и хрупкость (и падение при офлайне). Кэш заполняет отдельный
sync-шаг, раннер работает офлайн и детерминированно.

### Тесты

`tests/test_cloudru_prices.py`: парсинг каталога (mock httpx), запись/чтение и TTL,
precedence cache > config > fallback, GigaChat3.5 → 96.22/288.6/0,
DeepSeek-V4.1-Flash → 64.94/194.81/6.5, unknown → fallback + warning.
