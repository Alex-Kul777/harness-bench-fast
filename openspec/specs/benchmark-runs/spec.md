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

#### Scenario: OpenClaw-раннер агрегирует шаги

- **WHEN** `run_openclaw_bench.py` записывает артефакт прогона в `_write_results(...)`
- **THEN** блок `summary` SHALL содержать `total_steps`, равный сумме per-task
  `agent_steps` (число вызовов инструментов), а SHALL NOT опускать это поле

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

### Requirement: Pi-раннер опирается на санитарный timeout

Поскольку базовый `pi-agent` не предоставляет управление лимитом шагов, Pi-раннер
SHALL использовать санитарный `--timeout` как единственный ограничитель времени
прогона и SHALL NOT эмулировать лимит шагов (синтетический счётчик или подмену на
иной механизм).

#### Scenario: Ограничение прогона

- **WHEN** `run_pi_bench.py` запускает задачу
- **THEN** ограничение SHALL задаваться только через `--timeout` (плюс
  `--concurrency`), без какого-либо шаг-капа

#### Scenario: Запрос шаг-капа

- **WHEN** запрошен лимит шагов, не поддерживаемый базовым агентом
- **THEN** раннер SHALL NOT подменять его скрытой эмуляцией; ограничение
  документируется, а не имитируется

### Requirement: Эффективный таймаут с учётом floors задач

Pi-раннер SHALL вычислять эффективный таймаут задачи как
`max(--timeout, task.min_timeout_seconds)`, обрезая `task.max_timeout_seconds`
(семантика `effective_task_timeout`), и SHALL записывать эффективный таймаут в
JSON-результат прогона.

#### Scenario: Floor поднимает таймаут

- **WHEN** задача long с `min_timeout_seconds = 7200` запускается с `--timeout 2400`
- **THEN** эффективный таймаут SHALL быть `7200`, а не `2400`

#### Scenario: Max обрезает таймаут

- **WHEN** у задачи `min_timeout_seconds = max_timeout_seconds = 3600`, а передан `--timeout 7200`
- **THEN** эффективный таймаут SHALL быть `3600`

### Requirement: Таймаут ниже флора не применяется молча

Конечный `--timeout` ниже `task.min_timeout_seconds` SHALL отклоняться (задача
пропускается/поднимается до флора), если не задан явный opt-in; при opt-in прогон
SHALL помечаться как несопоставимый (`comparable: false`).

#### Scenario: Осознанный cost-cap

- **WHEN** задан `--allow-below-floor` с таймаутом ниже флора
- **THEN** задача выполняется, но результат SHALL быть помечен несопоставимым

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
