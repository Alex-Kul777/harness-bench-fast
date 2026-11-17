## ADDED Requirements

### Requirement: Детекция инфраструктурного краха OC-раннера

`run_openclaw_bench.run_one_task` SHALL помечать per-task запись `harness_error: true`,
когда завершение относится к инфраструктурному краху харнесса, а не к провалу модели.
Детекция SHALL NOT делать задачу пройденной.

#### Scenario: Listener leak помечает задачу

- **WHEN** `openclaw agent exec` завершается с `returncode != 0`, `stderr` содержит
  `MaxListenersExceededWarning`, а `usage` отсутствует
- **THEN** per-task запись SHALL содержать `harness_error: true`, а `passed` SHALL остаться `false`

#### Scenario: Обычный провал модели не помечается

- **WHEN** харнесс завершился с `returncode == 0` либо с валидным ненулевым `usage`
  без crash-маркеров в `stderr`
- **THEN** per-task запись SHALL NOT содержать `harness_error: true`

### Requirement: Признаки и вид инфраструктурного краха

Крах SHALL определяться по crash-маркеру из константы `HARNESS_CRASH_MARKERS`
(`MaxListenersExceededWarning`, `EventEmitter memory leak`,
`Use emitter.setMaxListeners`, `connect listeners added`) в `stderr`; дополнительно —
при `returncode != 0` с нулевым/отсутствующим `usage`. Запись SHALL содержать
`harness_error_kind` ∈ {`listener_leak`, `provider_transport`, `unknown`}.

#### Scenario: Вид краха записан

- **WHEN** задача помечена `harness_error: true`
- **THEN** `harness_error_kind` SHALL присутствовать и равняться одному из допустимых значений

#### Scenario: Контентный 403 без нулевого usage не считается крахом

- **WHEN** в ошибке присутствует `403`/`sensitive information`, но `usage` ненулевой
- **THEN** задача SHALL NOT помечаться как `harness_error`

### Requirement: Маркер harness-краха в summary прогона

`run_openclaw_bench._write_results` SHALL записывать в `summary` число
`harness_errors` (сколько per-task записей имеют `harness_error: true`) и список
`harness_error_tasks` (их `task_id`). Поля SHALL присутствовать всегда (0 / пустой список
при отсутствии крахов) и SHALL NOT выдумывать токены/стоимость для крашнутых задач.

#### Scenario: Счётчик крахов в summary

- **WHEN** из N задач одна помечена `harness_error: true`
- **THEN** `summary.harness_errors` SHALL равняться `1`, а `summary.harness_error_tasks`
  SHALL содержать её `task_id`

#### Scenario: Нет крахов

- **WHEN** ни одна задача не помечена `harness_error`
- **THEN** `summary.harness_errors` SHALL равняться `0`, а `summary.harness_error_tasks` —
  пустому списку

### Requirement: Несопоставимость прогона с harness-крахом

Прогон, содержащий хотя бы одну задачу с `harness_error: true`, SHALL помечаться
`summary.comparable = false`; прогон без крахов SHALL иметь `comparable = true`.
Несопоставимые прогоны SHALL NOT учитываться как честные провалы модели.

#### Scenario: Прогон с крахом несопоставим

- **WHEN** `summary.harness_errors > 0`
- **THEN** `summary.comparable` SHALL равняться `false`

#### Scenario: Чистый прогон сопоставим

- **WHEN** `summary.harness_errors == 0`
- **THEN** `summary.comparable` SHALL равняться `true`

#### Scenario: Обратная совместимость

- **WHEN** артефакт не содержит полей `harness_errors`/`comparable` (старый прогон)
- **THEN** потребители SHALL трактовать его как `harness_errors = 0`, `comparable = true`
