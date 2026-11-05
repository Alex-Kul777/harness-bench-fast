# benchmark-runs (delta)

## ADDED Requirements

### Requirement: Выбор волны в раннерах

Раннеры Pi и OpenClaw SHALL поддерживать выбор волны по имени через флаг
`--suite`, где имена совпадают с ключами `harness_bench.tasks.SUITES`.

#### Scenario: Прогон новой волны по имени

- **WHEN** раннер запускается с `--suite reflect`
- **THEN** выбираются задачи волны tool-reflection (412–431) из registry v0.21.3,
  и запуск идёт без явного перечисления ID

#### Scenario: Приоритет явного списка

- **WHEN** заданы одновременно `--tasks` и `--suite`
- **THEN** SHALL использоваться явный список `--tasks`

#### Scenario: Неизвестное имя волны

- **WHEN** передан `--suite` со значением, которого нет в `SUITES`
- **THEN** раннер SHALL завершиться с ошибкой до запуска задач, перечислив допустимые имена
