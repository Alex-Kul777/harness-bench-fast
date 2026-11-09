# result-reporting (delta)

## ADDED Requirements

### Requirement: Канонические колонки и метаданные семпл-таба

Таблица `#medium-sample` на `docs/fork.html` SHALL использовать канонические колонки
форка (`Harness`, `Profile`, `Model`, `Result`, `%`, `Time`, `Steps`, `Tokens (cost)`)
наряду с колонками наших урезанных наборов (`Subset`, `Coverage`, `Status`). Строки
семпла SHALL проходить те же преобразования метаданных, что и строки `#medium`: дата в
`Profile`, уровень ризонинга и провайдер в `Model`, версия в `Harness`.

#### Scenario: Колонка Steps в семпл-табе

- **WHEN** таблица `#medium-sample` отрисовывается
- **THEN** она SHALL содержать колонку `Steps` (значение `—` только при отсутствии шагов
  во всех источниках)

#### Scenario: Дата в Profile семпла

- **WHEN** для строки семпла доступна дата прогона
- **THEN** `Profile` SHALL отображаться как `профиль (YYYY-MM-DD)`

#### Scenario: Версия в Harness семпла

- **WHEN** артефакт прогона строки семпла содержит `harness_version`
- **THEN** `Harness` SHALL отображаться как `харнес версия`

#### Scenario: Провайдер и уровень в Model семпла

- **WHEN** строка семпла принадлежит нашему прогону с ризонингом
- **THEN** `Model` SHALL отображаться как `модель (cloud.ru) (уровень)`

## MODIFIED Requirements

### Requirement: Уровень ризонинга в колонке Model

Колонка `Model` наших строк на `docs/fork.html` SHALL включать провайдера и уровень
ризонинга из профиля прогона в формате `модель (провайдер) (уровень)` (напр.
`DeepSeek-V4.1-Flash (cloud.ru) (thinking: high)`), зеркаля upstream (напр.
`DeepSeek V4.1 Flash (OpenRouter) (high)`). Для наших строк провайдер — `cloud.ru`. Для
профилей без ризонинга (`MCP off`, `—`) суффикс уровня SHALL отсутствовать.

#### Scenario: Профиль с ризонингом

- **WHEN** профиль прогона содержит уровень ризонинга (`thinking: off`, `high`, …)
- **THEN** `Model` SHALL отображаться как `модель (провайдер) (уровень)`

#### Scenario: Профиль без ризонинга

- **WHEN** профиль не описывает ризонинг (`MCP off`, `—`)
- **THEN** `Model` SHALL отображаться без суффикса ризонинга

#### Scenario: Провайдер неизвестен

- **WHEN** провайдер строки не определён
- **THEN** `Model` SHALL отображаться без суффикса провайдера (значение SHALL NOT
  выдумываться)
