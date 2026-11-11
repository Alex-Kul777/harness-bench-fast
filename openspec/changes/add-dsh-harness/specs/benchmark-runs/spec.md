# benchmark-runs (delta)

## ADDED Requirements

### Requirement: Раннер DeepSeek Harness (dsh)

Система SHALL предоставлять раннер `run_dsh_bench.py`, который выполняет каждую
задачу harness-bench-fast через официальный harness DeepSeek AI (`dsh`) в режиме
`headless` с машинно-читаемым выводом `--json`, в изолированном рабочем каталоге
задачи, с провайдер-роутом Cloud.ru, инжектированным временным patch-файлом, и
SHALL NOT помещать секрет в аргументы командной строки.

#### Scenario: Headless-запуск задачи

- **WHEN** раннер запускает задачу
- **THEN** он SHALL вызвать `dsh --profile headless --patch <patch.yml>
  --permission-mode <preset> --json '<task>'` с `cwd` = рабочего каталога задачи

#### Scenario: Изоляция и креды

- **WHEN** раннер запускает `dsh`
- **THEN** окружение SHALL задавать изолированный `DSH_HOME` и `DSH_BENCH_API_KEY`,
  разрешённый через `resolve_bench_api_key()`, а сам ключ SHALL NOT попадать в argv

#### Scenario: Bare model id

- **WHEN** передан ид с провайдер-префиксом (например
  `custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash`)
- **THEN** в patch SHALL записываться bare-ид (`deepseek-ai/DeepSeek-V4.1-Flash`)

#### Scenario: Уровень reasoning

- **WHEN** передан `--thinking <level>`
- **THEN** провайдер-роут в patch SHALL получать `reasoning: <level>`, где
  `none`/`off` оба отображаются в `off`, а значение по умолчанию — `off`

### Requirement: Usage из `status.step_end`

Раннер SHALL брать токен-бакеты из событий `status.step_end.usage` потока `--json`
и суммировать их по всем шагам; `steps` SHALL равняться числу событий `step_end`,
а `reason`/финальный текст — из события `final`.

#### Scenario: Суммирование usage

- **WHEN** поток содержит несколько событий `status.step_end` с полем `usage`
- **THEN** `agent_input_tokens`/`agent_output_tokens`/`agent_total_tokens`/
  `agent_cache_read_tokens`/`agent_cache_write_tokens` SHALL быть суммами
  соответствующих полей по всем `step_end`

#### Scenario: Пройденная задача

- **WHEN** задача завершается
- **THEN** `passed` SHALL быть истинным только если код выхода равен 0, и
  `final.reason.kind` равен `completed`, и верификатор задачи прошёл

### Requirement: Регистрация харнесса dsh в форк-метаданных

`scripts/fork_metadata.py` SHALL распознавать стемы раннера как харнесс
`DeepSeek Harness`: `HARNESS_PREFIXES` SHALL содержать `("dsh_", "DeepSeek Harness")`,
а `classify_harness`/`resolve_stem` SHALL резолвить стем `dsh_shotlist_ds41flash_...`.

#### Scenario: Классификация стема dsh

- **WHEN** на вход подан стем `dsh_shotlist_ds41flash_high_20261111`
- **THEN** `classify_harness` SHALL вернуть `DeepSeek Harness`, а `resolve_stem` —
  харнесс `DeepSeek Harness`, модель `DeepSeek-V4.1-Flash` и уровень `high`

### Requirement: Artifact-шапка прогона dsh

Раннер SHALL записывать JSON-артефакт с top-level шапкой через
`harness_bench.artifact_metadata(harness="dsh", ...)` (поля `harness`, `thinking`,
`model`, `harness_version`) и блоком `summary` с
`total_input_tokens`/`total_output_tokens`/`total_tokens`/`total_steps`/
`total_cache_read_tokens`/`total_cache_write_tokens`/`estimated_cost_rub`/
`bench_credential`, а per-task строки SHALL нести `agent_*` поля и `session_id`.

#### Scenario: Запись артефакта

- **WHEN** прогон записывается в `--json-output`
- **THEN** top-level `harness` SHALL быть `dsh`, `thinking` SHALL отражать `--thinking`,
  `harness_version` SHALL быть взят из `dsh --version`, а `summary` SHALL содержать
  перечисленные поля, включая `bench_credential`

#### Scenario: Стоимость по ставкам модели

- **WHEN** для модели есть ставки
- **THEN** `estimated_cost_rub` SHALL вычисляться через `resolve_model_rates`/
  `compute_cost_rub`, иначе стоимость SHALL быть 0 и результат помечен
  (`rates_available: false`), а не рассчитан молча
