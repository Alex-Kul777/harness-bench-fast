# Design: fix-runner-cost-rates

## ADR-inline

**Решение:** создать `harness_bench/cost_resolver.py` с функцией
`resolve_model_rates(model_id, config_path=None) -> dict`.

### Алгоритм resolver

1. Прочитать `config_path` (или `$OPENCLAW_CONFIG`, или `~/.openclaw/openclaw.json`).
2. Обойти `models.providers.<provider>.models[]`, искать точное совпадение составного
   id `<provider>/<model>` с переданным `model_id`.
3. Вернуть dict `{input, output, cacheRead, cacheWrite}` (₽/1M).
4. Fallback: если модель не найдена — вернуть дефолт GLM-5.2
   `{input: 239.12, output: 751.52, cacheRead: 0.0, cacheWrite: 0.0}` и залогировать
   предупреждение.

### Формула стоимости

```
cost_rub = (
    input_tokens / 1e6 * rates["input"]
  + output_tokens / 1e6 * rates["output"]
  + cache_read_tokens / 1e6 * rates["cacheRead"]
  + cache_write_tokens / 1e6 * rates["cacheWrite"]
)
```

### Preferred path (openclaw per-task cost)

Если OpenClaw runner возвращает `agent_cost_usd` (нативная стоимость задачи),
она НЕ пересчитывается дополнительно — используется как есть (конвертация USD→RUB
не входит в scope; ₽-аккаунтинг через токены достаточен для аудита).

### Workaround для совместимости

Все три раннера содержат модульные константы. Заменяем их на вызов resolver в начале
скрипта — поведение остаётся идемпотентным при запуске без openclaw.json (fallback).

## Тесты

- Unit: `resolve_model_rates("custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash")` == 64.94/194.81/6.5/0
- Unit: GLM-5.2 == 239.12/751.52
- Golden: реплицировать 201.62 ₽ из аудита
- Backfill smoke: корректная обработка JSON без summary
