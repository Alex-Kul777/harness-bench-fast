# result-reporting (delta)

## ADDED Requirements

### Requirement: Уровень ризонинга в колонке Model

Колонка `Model` наших строк на `docs/fork.html` SHALL включать уровень ризонинга из профиля
прогона в формате `модель (уровень)` (напр. `GLM-5.2 (thinking: off)`, `GLM-5.2 (high)`),
зеркаля upstream (напр. `DeepSeek V4.1 Flash (OpenRouter) (high)`). Для профилей без
ризонинга (`MCP off`, `—`) суффикс SHALL отсутствовать.

#### Scenario: Профиль с ризонингом

- **WHEN** профиль прогона содержит уровень ризонинга (`thinking: off`, `high`, …)
- **THEN** `Model` SHALL отображаться как `модель (уровень)`

#### Scenario: Профиль без ризонинга

- **WHEN** профиль не описывает ризонинг (`MCP off`, `—`)
- **THEN** `Model` SHALL отображаться без суффикса ризонинга

### Requirement: Версия харнеса в колонке Harness

Колонка `Harness` наших строк SHALL включать версию харнеса (`харнес версия`) **когда она
записана в артефакте прогона** (`harness_version`/`openclaw_version`/`cli_version`/
`runner_version`), зеркаля upstream (`pi-mono 0.73.1`). При отсутствии записи суффикс SHALL
отсутствовать (версии SHALL NOT выдумываться).

#### Scenario: Версия записана

- **WHEN** артефакт прогона содержит поле версии харнеса
- **THEN** `Harness` SHALL отображаться как `харнес версия`

#### Scenario: Версия не записана

- **WHEN** артефакт не содержит версии харнеса
- **THEN** `Harness` SHALL отображаться без суффикса (значение SHALL NOT выдумываться)
