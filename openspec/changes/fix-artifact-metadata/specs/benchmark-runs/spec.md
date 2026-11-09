# benchmark-runs (delta)

## ADDED Requirements

### Requirement: Полная метаданных-шапка артефакта прогона

Артефакт прогона SHALL содержать top-level поля с точными именами: `harness`
(строка), `harness_version` (строка), `thinking` (строка — уровень reasoning),
`task_set_version` (строка) и `model` (строка). Раннеры Pi, OpenClaw и Hermes
SHALL записывать этот набор через общий helper `harness_bench.artifact_metadata`.

#### Scenario: Все поля записаны

- **WHEN** любой из трёх раннеров записывает артефакт прогона через `_write_results`
- **THEN** артефакт SHALL содержать top-level `harness`, `thinking`, `task_set_version` и `model` как строки

#### Scenario: Уровень reasoning задан

- **WHEN** прогон запущен с явным уровнем reasoning (например `--thinking high`)
- **THEN** поле `thinking` SHALL равняться этому уровню

#### Scenario: Уровень reasoning не задан

- **WHEN** уровень reasoning не задан явно
- **THEN** поле `thinking` SHALL равняться строке `"default"`

#### Scenario: Версия харнесса известна

- **WHEN** версия харнесса задана флагом, env или autodetect
- **THEN** поле `harness_version` SHALL присутствовать и равняться этой версии

#### Scenario: Версия харнесса неизвестна

- **WHEN** ни флаг, ни env, ни autodetect не дали версию харнесса
- **THEN** поле `harness_version` SHALL отсутствовать в артефакте (SHALL NOT выдумываться)

### Requirement: Корректная версия набора задач для волны

Раннеры SHALL выводить `task_set_version` из задач прогона через ревизии
`harness_bench.versioning.TASK_SET_REVISIONS`, а не из хардкод-константы. Для
прогонов waves 17–19 (задачи 392–471) записанная `task_set_version` SHALL NOT
равняться `"0.16.0"` и SHALL соответствовать версии этой волны.

#### Scenario: Wave 17–19 не записывается как 0.16.0

- **WHEN** конфиг прогона содержит задачи из waves 17–19 (диапазон 392–471)
- **THEN** записанная `task_set_version` SHALL NOT быть `"0.16.0"` и SHALL равняться версии соответствующей волны

#### Scenario: Light остаётся 0.16.0

- **WHEN** прогон содержит только задачи Light (1–391)
- **THEN** записанная `task_set_version` SHALL равняться `"0.16.0"`

#### Scenario: Пустой набор задач

- **WHEN** список задач пуст или номера задач не распознаны
- **THEN** раннер SHALL записать текущую `TASK_SET_VERSION` реестра
