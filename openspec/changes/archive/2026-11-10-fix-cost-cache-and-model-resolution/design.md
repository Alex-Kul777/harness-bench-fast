# Design: fix-cost-cache-and-model-resolution

## ADR-inline

**Решение:** cache-read бакет восстанавливается из `total_tokens`, а неопределимая
модель разрешается по подсказке из имени файла — обе операции в одном месте
(`harness_bench/cost_resolver.py`), раннер и бэкфилл только вызывают его.

### Восстановление cache-read

`total_tokens = input + output + cache_read + cache_write`. Если явные cache-поля
отсутствуют (и их сумма = 0), но известен `total_tokens`:

```
cache_read = max(total_tokens - input - output, 0)
```

Если явное cache-поле присутствует — используется как есть (не перезаписывается).

### Разрешение модели

Прецеденция `resolve_model_rates(model_id, filename=None)`:

1. catalog cache `~/.openclaw/cloudru-prices.json` (точное или суффиксное совпадение),
2. `cost`-блоки `~/.openclaw/openclaw.json`,
3. подсказка из имени файла (карта `gigachat3pro|giga35|glm52|glm53|qwen36|oss120b|minimaxm3|ds41flash`),
   найденный id проходит шаги 1–2 заново,
4. fallback GLM-5.2 (239.12/751.52/0/0) + WARNING в stderr.

Явные поля артефакта по-прежнему приоритетнее имени файла: бэкфилл сначала пробует
поля, и только если модель не определена — resolver использует `filename`.

### Тесты

- `tests/test_cost_cache_bucket.py` — реальный артефакт: `estimated_cost_rub` тарифицирует
  cache-read бакет (≈572.89 ₽, не 406.76 ₽).
- `tests/test_cost_filename_hints.py` — `resolve_model_rates("", filename="pi_shotlist_gigachat3pro.json")`
  возвращает ставки `GigaChat/GigaChat-3-Pro` (73.03/176.39), а не fallback.

Оба теста «красные» до фикса и «зелёные» после.
