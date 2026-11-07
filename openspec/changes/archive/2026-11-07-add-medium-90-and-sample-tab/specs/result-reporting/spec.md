# result-reporting (delta)

## MODIFIED Requirements

### Requirement: Единая форк-страница

Форк SHALL публиковать наши результаты одной страницей `docs/fork.html` (+ данные
`docs/fork-home-results.json`, генератор `scripts/build_fork_home.py`) с наборами
Shot List (52), Light (391), **Medium (90)** и **Medium sample** — переключаемыми
табами на одном URL. Таблицы конфигов SHALL иметь ровно девять колонок; активный таб
SHALL следовать URL-hash (`#shotlist` / `#light` / `#medium` / `#medium-sample`).

#### Scenario: Единая страница отображается

- **WHEN** открывается `docs/fork.html`
- **THEN** SHALL присутствовать четыре таба-набора и таблица активного набора

#### Scenario: Табы переключают набор

- **WHEN** пользователь выбирает таб (Shot List / Light / Medium / Medium sample)
- **THEN** SHALL отображаться ровно этот набор, а URL-hash SHALL становиться
  `#shotlist` / `#light` / `#medium` / `#medium-sample` (`aria-pressed` отражает активный таб)

#### Scenario: Ровно девять колонок

- **WHEN** таблица конфигов набора отображается
- **THEN** её заголовок SHALL содержать ровно девять колонок
  (`Harness`, `Profile`, `Model`, `Result`, `%`, `Time`, `Steps`, `Tokens (cost)`, `Version`),
  а `ours`/`upstream` SHALL разделяться групповыми строками, не колонкой

#### Scenario: Version заполнена

- **WHEN** строка отображается
- **THEN** `Version` SHALL содержать task-set version (наши) или `source_version` (upstream),
  либо `—` при отсутствии

#### Scenario: Волновая разбивка Medium

- **WHEN** активен таб Medium
- **THEN** волновая разбивка (long / reflect / feasibility / composite hard) SHALL быть
  доступна в раскрывающемся блоке `details`

#### Scenario: Старые URL не ломаются

- **WHEN** открывается `fork-medium90.html` или `fork-light.html`
- **THEN** он SHALL перенаправлять на `docs/fork.html#medium` / `#light`, активируя нужный таб

## ADDED Requirements

### Requirement: Полный Medium на форк-странице

Таб `#medium` SHALL показывать полный набор Medium (90 задач: historical 392–471 плюс
wave 21 512–530). Наши прогоны с неполным покрытием SHALL попадать в таблицу с видимой
пометкой `partial` и опорным знаменателем 90.

#### Scenario: Неполный охват виден

- **WHEN** наш прогон покрывает только часть 90 задач
- **THEN** ячейка `Result` SHALL показывать `X/Y (partial Y/90)`, а строка SHALL попадать
  в таблицу `#medium`

#### Scenario: Знаменатель 90 и апстрим из 90-борда

- **WHEN** таблица `#medium` отображается
- **THEN** полный набор SHALL задавать знаменатель 90 (включая wave21), а апстрим-строки
  SHALL браться из 90-задачного борда (`docs/medium90-results.json`)

### Requirement: Урезанный Medium-семпл

Форк SHALL публиковать таб `#medium-sample` с нашими урезанными Medium-наборами
(суммарный охват прогнанных задач и пилоты) из манифеста, показывая неполное покрытие
относительно 90.

#### Scenario: Семпл-таб доступен

- **WHEN** открывается `docs/fork.html#medium-sample`
- **THEN** SHALL отображаться таблица наших наборов с колонкой `Coverage`
  (например `66/90`, `13/90`)

#### Scenario: Пилот помечен урезанным

- **WHEN** строка — пилот
- **THEN** её `Status`/`Coverage` SHALL показывать, что охват неполный (например
  `pilot (truncated)`, `13/90`), а источник SHALL быть в манифесте
