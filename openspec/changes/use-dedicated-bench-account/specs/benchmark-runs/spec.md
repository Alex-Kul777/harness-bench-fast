## ADDED Requirements

### Requirement: Выделенный бенч-ключ для всех моделей и харнессов

Раннеры бенчмарка (Pi, OpenClaw, Hermes) SHALL резолвить Cloud.ru API-ключ через
общий helper `harness_bench.bench_credentials.resolve_bench_api_key()` с приоритетом
`CLOUD_RU_BENCH_API_KEY` → `CLOUD_RU_KAP_HERMES` (env, затем `~/.hermes/.env`) →
production `CLOUD_RU_API_KEY`, чтобы все модели и харнессы оплачивались выделенным
бенч-аккаунтом. Когда `CLOUD_RU_BENCH_API_KEY` задан, раннеры SHALL NOT использовать
production-ключ `CLOUD_RU_API_KEY`.

#### Scenario: Выделенный ключ имеет приоритет

- **WHEN** заданы и `CLOUD_RU_BENCH_API_KEY`, и production `CLOUD_RU_API_KEY`
- **THEN** раннер SHALL использовать ключ из `CLOUD_RU_BENCH_API_KEY`, а SHALL NOT
  использовать production `CLOUD_RU_API_KEY`

#### Scenario: Мягкий fallback при отсутствии выделенного ключа

- **WHEN** `CLOUD_RU_BENCH_API_KEY` не задан
- **THEN** раннер SHALL откатиться на `CLOUD_RU_KAP_HERMES` (env, затем `~/.hermes/.env`),
  а при его отсутствии — на `CLOUD_RU_API_KEY`, с предупреждением в stderr

#### Scenario: Отличимый NOTE об источнике

- **WHEN** `resolve_bench_api_key` выбирает источник ключа
- **THEN** он SHALL вывести в stderr NOTE, различающий источники
  (`CLOUD_RU_BENCH_API_KEY` / `CLOUD_RU_KAP_HERMES` / production fallback),
  а SHALL NOT печатать значение ключа

#### Scenario: Hermes-раннер не берёт production первым

- **WHEN** `run_hermes_bench.py` формирует окружение для `--provider custom`
- **THEN** `OPENAI_API_KEY` SHALL браться из результата `resolve_bench_api_key()`,
  а SHALL NOT из production `CLOUD_RU_API_KEY` первым

#### Scenario: OpenClaw-раннер прокидывает ключ в окружение

- **WHEN** `run_openclaw_bench.py` запускает `openclaw agent exec`
- **THEN** резолвнутый бенч-ключ SHALL быть добавлен в дочернее окружение вызова
  (`CLOUD_RU_API_KEY`/`CLOUD_RU_BENCH_API_KEY`), не ломая конфиг-провайдер

### Requirement: Источник ключа в артефакте прогона

Артефакт прогона SHALL фиксировать, какой источник ключа оплатил прогон, в
`summary.bench_credential` (имя env-переменной или `none`), не ломая существующий
контракт `summary` и автосинк `scripts/build_fork_results.py`.

#### Scenario: Источник записан

- **WHEN** любой из трёх раннеров записывает артефакт прогона через `_write_results`
- **THEN** `summary.bench_credential` SHALL равняться имени выбранной env-переменной
  источника ключа

#### Scenario: Контракт автосинка не ломается

- **WHEN** артефакт содержит `summary.bench_credential`
- **THEN** `scripts/build_fork_results.py --check` SHALL оставаться успешным (== 0),
  а существующие поля `summary` SHALL NOT меняться
