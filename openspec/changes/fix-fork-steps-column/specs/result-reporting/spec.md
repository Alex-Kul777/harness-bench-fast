# result-reporting (delta)

## ADDED Requirements

### Requirement: Заполнение колонки Steps

Колонка `Steps` в таблицах результатов форка SHALL заполняться значением шагов агента:
сначала агрегат `summary.total_steps`, затем top-level `steps`, затем fallback — сумма
per-task `agent_steps` из `tasks[]`. Значение `—` SHALL показываться только если шаги
отсутствуют во всех источниках.

#### Scenario: Агрегат отсутствует, per-task данные есть

- **WHEN** JSON-прогон не содержит `summary.total_steps` и top-level `steps`, но в `tasks[]`
  есть `agent_steps`
- **THEN** колонка `Steps` SHALL показывать сумму `agent_steps` (а SHALL NOT показывать `—`)

#### Scenario: Агрегат присутствует

- **WHEN** JSON-прогон содержит `summary.total_steps`
- **THEN** колонка `Steps` SHALL показывать значение агрегата (без пересчёта)

#### Scenario: Данных нет вовсе

- **WHEN** шаги отсутствуют и в агрегате, и в per-task записях
- **THEN** колонка `Steps` SHALL показывать `—`

#### Scenario: Единый источник для обеих поверхностей

- **WHEN** запускаются `scripts/build_fork_home.py` и `scripts/build_fork_results.py`
- **THEN** обе поверхности SHALL применять одинаковый приоритет источников и давать
  согласованное значение `Steps` для одного и того же прогона
