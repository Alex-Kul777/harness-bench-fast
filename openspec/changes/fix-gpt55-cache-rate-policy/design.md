# Design: fix-gpt55-cache-rate-policy

## ADR-inline — синтетическая/неверная публичная cache-ставка → входная ставка

**Контекст.** Факт-биллинг Cloud.ru для gpt-5.5: `cost = input*854 + output*5124`, где
`input` — полный prompt, включая cached (подтверждено ±0,02% по провайдерской выгрузке;
см. `tests/fixtures/gpt55_provider_slice.csv`). Публикуемая `cache_read = 85.4` равна
`input/10` и занижает стоимость.

**Решение.** Расширяем политику H2: кэш-бакет тарифицируется по входной ставке не только
когда публичного cache-тарифа **нет**, но и когда публичный тариф **синтетический/неверен**.
Реализация — явная таблица `CACHE_RATE_OVERRIDES: {model_id: "input" | ₽/1M}`:

```python
CACHE_RATE_OVERRIDES = {"openai/gpt-5.5": "input"}
```

Override применяется в `resolve_model_rates` через `_finalize_rates`
(`_apply_cache_rate_override` + `_note_cache_tariff`) после любой успешной ветки
(каталог / config / filename-подсказка), поэтому его видят и раннер, и бэкфилл
(`compute_cost_rub` → `cache_rate_or_input` берёт уже подменённый `cacheRead`).

**Почему явная таблица, а не эвристика `cache == input/10`.** Отношение `input/10` (10%
от входной ставки) — легитимная схема дисконта кэша у ряда провайдеров. Автодетект по
ratio переоценил бы такие модели и сделал бы политику неявной. Явный, аудируемый список
безопасен для остальных моделей и добавляется только после доказанного расхождения с
фактом биллинга.

**Совместимость.** DeepSeek-V4.1-Flash (`cache_read = 6.5`) не в таблице → сохраняется как
есть. Публично опубликованные ₽ gpt-5.5 (сумма **61 966,63 ₽**, cache@input) не меняются;
стандартный бэкфилл теперь даёт ту же цену и не откатывает их.

**Notes (различение).** При срабатывании override resolver печатает
`[cost_resolver] NOTE: cache-rate override for '<model>': the published cache tariff
(N ₽/1M) is synthetic/incorrect; pricing cache tokens at the INPUT rate (M ₽/1M).`
Для моделей без cache-тарифа сохраняется прежний NOTE (H2), для публичной корректной
ставки — тишина.

## Свидетельства

- `resolve_model_rates("openai/gpt-5.5")` → `cacheRead = 854.0` (было 85.4).
- `scripts/backfill_cost_rub.py results --dry-run` → gpt-5.5 строки `same → same`,
  итог `0 updated, 64 unchanged` (до фикса строки уходили в `→ 4052.40 ₽` и т.п.).
- Сумма gpt-5.5 (10 артефактов `results/*gpt55*20261110.json`) = **61 966,63 ₽** (до и после).
