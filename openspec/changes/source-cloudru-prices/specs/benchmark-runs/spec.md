## MODIFIED Requirements

### Requirement: Per-model ₽ pricing

Раннеры SHALL определять ставки стоимости (input / output / cacheRead / cacheWrite ₽ за 1M токенов) через resolver, а не через хардкод констант, и SHALL включать cache-read и cache-write токены в формулу `estimated_cost_rub`, когда эти поля присутствуют в usage-ответе.

#### Scenario: Ставки берутся из resolver

- **WHEN** раннер считает `estimated_cost_rub` для прогона
- **THEN** ставки SHALL приходить из resolver, а SHALL NOT из хардкод-константы

#### Scenario: Cache-read включён в стоимость

- **WHEN** прогон содержит cache-read токены
- **THEN** они SHALL учитываться в `estimated_cost_rub` по ставке `cacheRead` модели

### Requirement: Приоритет источников ставок

Resolver SHALL резолвить ставки в порядке приоритета: (1) запись каталог-кэша Cloud.ru, (2) блок `cost` из `~/.openclaw/openclaw.json` (или `$OPENCLAW_CONFIG`), (3) задокументированный fallback GLM-5.2 (239.12/751.52/0/0) с предупреждением в stderr. Отсутствующее в источнике поле `cache_read` SHALL трактоваться как 0.

#### Scenario: Ставки из живого каталога

- **WHEN** каталог-кэш содержит запись для модели прогона
- **THEN** resolver SHALL вернуть ставки из кэша и SHALL NOT обращаться к блоку `cost` конфига

#### Scenario: Fallback на конфиг

- **WHEN** записи в каталог-кэше нет, но блок `cost` есть в openclaw.json
- **THEN** resolver SHALL вернуть ставки из конфига

#### Scenario: Явный fallback при отсутствии источников

- **WHEN** ни кэш, ни конфиг не содержат модель
- **THEN** resolver SHALL вернуть fallback-ставки и SHALL вывести WARNING в stderr

#### Scenario: Отсутствующее поле cache_read

- **WHEN** запись источника содержит input/output, но не содержит cache_read
- **THEN** resolver SHALL вернуть cacheRead равным 0

## ADDED Requirements

### Requirement: Синхронизация каталога ставок Cloud.ru

Система SHALL предоставлять скрипт `scripts/sync_cloudru_prices.py`, который тянет `GET https://foundation-models.api.cloud.ru/v1/models` и пишет кэш `{fetched_at, models}` в `~/.openclaw/cloudru-prices.json` по умолчанию, с поддержкой `--out` и `--ttl`. При сетевой или HTTP-ошибке скрипт SHALL NOT перезаписывать прежний кэш и SHALL завершаться ненулевым кодом.

#### Scenario: Успешная синхронизация

- **WHEN** каталог доступен и содержит модели
- **THEN** скрипт SHALL записать кэш с `fetched_at` и ставками `{input, output, cache_read, is_billable}` по каждой модели

#### Scenario: Ошибка сети сохраняет прежний кэш

- **WHEN** запрос каталога падает (сеть или HTTP-ошибка)
- **THEN** скрипт SHALL оставить прежний файл кэша нетронутым и SHALL выйти с ненулевым кодом
