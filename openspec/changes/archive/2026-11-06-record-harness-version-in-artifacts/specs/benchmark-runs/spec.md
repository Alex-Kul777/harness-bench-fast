# benchmark-runs (delta)

## ADDED Requirements

### Requirement: Версия харнеса в артефакте

Артефакт прогона SHALL содержать поле верхнего уровня `harness_version` (строка), когда
версия харнеса задана. Раннер `run-cli` SHALL принимать версию через флаг
`--harness-version` и через переменную окружения `HARNESS_BENCH_HARNESS_VERSION`
(флаг приоритетнее). При отсутствии значения поле SHALL отсутствовать в артефакте (версия
SHALL NOT выдумываться).

#### Scenario: Версия задана флагом

- **WHEN** `run-cli` запущен с `--harness-version "pi-mono 0.73.1"`
- **THEN** записанный артефакт SHALL содержать `harness_version = "pi-mono 0.73.1"`

#### Scenario: Версия задана через окружение

- **WHEN** задан `HARNESS_BENCH_HARNESS_VERSION` и флаг не передан
- **THEN** значение SHALL попасть в `harness_version` артефакта

#### Scenario: Версия не задана

- **WHEN** ни флаг, ни env не заданы
- **THEN** поле `harness_version` SHALL отсутствовать в артефакте

#### Scenario: Изоляция между прогонами

- **WHEN** прогон завершился (успешно или с прерыванием)
- **THEN** установленное значение версии SHALL сбрасываться (не утекает в следующий прогон
  в том же процессе)
