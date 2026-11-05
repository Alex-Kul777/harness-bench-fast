# benchmark-runs

## Purpose

Определяет, как форк запускает бенчмарк-прогоны (Light 391, Medium 90, wave 19 —
задачи 432–471) на харнессах Pi / OpenClaw / Hermes / opencode и как результаты
сохраняются для последующей публикации.

## Requirements

### Requirement: Выбор suite

Система SHALL поддерживать выбор suite: `light` (задачи 1–391), `medium` (90 задач)
и явный диапазон задач для wave 19 (`432–471`).

#### Scenario: Запуск Light

- **WHEN** пользователь запускает раннер с `--suite light`
- **THEN** прогоняются задачи 1–391, и результат сохраняется как JSON с блоком `summary`

#### Scenario: Wave 19 требует изоляции

- **WHEN** выборка содержит задачи 432–471
- **THEN** запуск SHALL требовать Linux/bwrap-изоляцию (`--isolation bwrap`) и SHALL
  отклоняться до вызова модели при её отсутствии

### Requirement: Единый формат результата

Каждый прогон SHALL сохранять JSON с top-level `summary`: `passed`, `total`,
`pass_rate`, `total_seconds`, `total_steps`, `total_tokens`, `estimated_cost_rub`.

#### Scenario: Отчёт подхватывается автосинком

- **WHEN** прогон сохранён в каталоге `results/`
- **THEN** `scripts/build_fork_results.py` SHALL включать его в авто-блок, если имя
  файла совпадает с разрешёнными паттернами и не входит в список исключений

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
