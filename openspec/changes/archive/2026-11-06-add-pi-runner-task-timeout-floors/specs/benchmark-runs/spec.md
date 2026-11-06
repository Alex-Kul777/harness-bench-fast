# benchmark-runs (delta)

## ADDED Requirements

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
