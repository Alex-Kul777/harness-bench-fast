# result-reporting (delta)

## ADDED Requirements

### Requirement: Light-вид форк-страниц

Форк SHALL публиковать наши полные прогоны Light (задачи 1–391) отдельным видом:
`docs/fork-light.html` + данные `docs/fork-light-results.json`, собранные генератором
`scripts/build_fork_light.py` из явного allow-list источников. Страница SHALL содержать
канонические колонки `Profile`, `Time`, `Steps`, `Tokens (cost)`, ссылки на исходные JSON
и отдельную таблицу upstream-Light-строк для сравнения.

#### Scenario: Генерация вида

- **WHEN** запускается `python3 scripts/build_fork_light.py`
- **THEN** SHALL создаваться `docs/fork-light-results.json` и `docs/fork-light.html`

#### Scenario: Canonical columns

- **WHEN** страница Light отображается
- **THEN** таблица наших прогонов SHALL содержать колонки `Profile`, `Time`, `Steps`,
  `Tokens (cost)`; отсутствующее значение SHALL отображаться как `—`

#### Scenario: Upstream-сравнение

- **WHEN** страница Light отображается
- **THEN** она SHALL содержать таблицу upstream-Light-строк (harness · model · passed/total),
  отсортированную по числу пройденных задач

#### Scenario: Ссылка с других видов

- **WHEN** открыта `docs/fork-medium90.html` или `docs/fork-sample.html`
- **THEN** они SHALL содержать ссылку на `docs/fork-light.html`
