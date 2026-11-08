## MODIFIED Requirements

### Requirement: Per-model ₽ pricing

Раннеры SHALL определять ставки стоимости (input / output / cacheRead / cacheWrite
₽ за 1M токенов) через resolver, читающий `~/.openclaw/openclaw.json` (или путь из
`$OPENCLAW_CONFIG`), а не через хардкод констант.

Раннеры SHALL включать cache-read и cache-write токены в формулу расчёта
`estimated_cost_rub`, когда соответствующие поля присутствуют в usage-ответе.

При отсутствии конфигурационного файла или при неизвестной модели раннер SHALL
использовать задокументированный fallback (GLM-5.2: 239.12/751.52/0/0) и SHALL
вывести предупреждение в stderr.

#### Scenario: Корректные ставки для DeepSeek-V4.1-Flash

- **WHEN** раннер запускается с `model=deepseek-ai/DeepSeek-V4.1-Flash`
- **THEN** `estimated_cost_rub` SHALL рассчитываться по ставкам 64.94/194.81/6.5/0 ₽/1M

#### Scenario: Cache-read включён в стоимость

- **WHEN** прогон содержит cache-read токены
- **THEN** они SHALL учитываться в `estimated_cost_rub` по ставке `cacheRead` модели

#### Scenario: Fallback при неизвестной модели

- **WHEN** модель не найдена в openclaw.json
- **THEN** раннер SHALL использовать ставки GLM-5.2 и SHALL вывести предупреждение в stderr

#### Scenario: Fallback при отсутствии конфига

- **WHEN** `~/.openclaw/openclaw.json` не существует и `$OPENCLAW_CONFIG` не задан
- **THEN** раннер SHALL использовать ставки fallback и SHALL продолжить работу без ошибки
