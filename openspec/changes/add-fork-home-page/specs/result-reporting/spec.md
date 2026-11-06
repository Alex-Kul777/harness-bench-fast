# result-reporting (delta)

## REMOVED Requirements

### Requirement: Light-вид форк-страниц

Отдельный вид `docs/fork-light.html` упраздняется — Light (391) теперь входит в единую
форк-страницу `docs/fork.html` (секция `#light`). Прежний URL сохраняется редиректом.

#### Scenario: Вид упразднён

- **WHEN** ранее публиковался `docs/fork-light.html`
- **THEN** он SHALL заменяться редиректом на `docs/fork.html#light`

## ADDED Requirements

### Requirement: Единая форк-страница

Форк SHALL публиковать наши результаты одной страницей `docs/fork.html` (+ данные
`docs/fork-home-results.json`, генератор `scripts/build_fork_home.py`) с тремя адресуемыми
секциями: Shot List (52), Light (391), Medium (80). Каждая секция SHALL содержать таблицу
в единой схеме колонок `Harness`, `Profile`, `Model`, `Result`, `%`, `Time`, `Steps`,
`Tokens (cost)`, `Version`, `Source`.

#### Scenario: Единая страница отображается

- **WHEN** открывается `docs/fork.html`
- **THEN** SHALL присутствовать три секции с анкорами `#shotlist`, `#light`, `#medium`,
  каждая с таблицей в единой схеме колонок

#### Scenario: Version заполнена

- **WHEN** строка отображается
- **THEN** `Version` SHALL содержать task-set version (наши) или `source_version` (upstream),
  либо `—` при отсутствии

#### Scenario: Старые URL не ломаются

- **WHEN** открывается прежний URL `fork-medium90.html` или `fork-light.html`
- **THEN** он SHALL перенаправлять на соответствующую секцию `docs/fork.html`
