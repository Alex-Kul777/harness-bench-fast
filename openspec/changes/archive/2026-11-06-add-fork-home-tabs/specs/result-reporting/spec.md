# result-reporting (delta)

## MODIFIED Requirements

### Requirement: Единая форк-страница

Форк SHALL публиковать наши результаты одной страницей `docs/fork.html` (+ данные
`docs/fork-home-results.json`, генератор `scripts/build_fork_home.py`) с тремя наборами —
Shot List (52), Light (391), Medium (80) — переключаемыми **табами** на одном URL. Каждая
таблица SHALL иметь ровно девять колонок, а активный таб SHALL следовать URL-hash.

#### Scenario: Единая страница отображается

- **WHEN** открывается `docs/fork.html`
- **THEN** SHALL присутствовать три таба-набора и таблица активного набора

#### Scenario: Табы переключают набор

- **WHEN** пользователь выбирает таб (Shot List / Light / Medium)
- **THEN** SHALL отображаться ровно этот набор, а URL-hash SHALL становиться
  `#shotlist` / `#light` / `#medium` (`aria-pressed` отражает активный таб)

#### Scenario: Ровно девять колонок

- **WHEN** таблица набора отображается
- **THEN** её заголовок SHALL содержать ровно девять колонок
  (`Harness`, `Profile`, `Model`, `Result`, `%`, `Time`, `Steps`, `Tokens (cost)`, `Version`),
  а `ours`/`upstream` SHALL разделяться групповыми строками, не колонкой

#### Scenario: Version заполнена

- **WHEN** строка отображается
- **THEN** `Version` SHALL содержать task-set version (наши) или `source_version` (upstream),
  либо `—` при отсутствии

#### Scenario: Волновая разбивка Medium

- **WHEN** активен таб Medium
- **THEN** волновая разбивка (long / reflect / feasibility) SHALL быть доступна в
  раскрывающемся блоке `details`

#### Scenario: Старые URL не ломаются

- **WHEN** открывается `fork-medium90.html` или `fork-light.html`
- **THEN** он SHALL перенаправлять на `docs/fork.html#medium` / `#light`, активируя нужный таб
