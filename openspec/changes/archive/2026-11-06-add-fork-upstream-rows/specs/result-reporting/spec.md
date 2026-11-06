# result-reporting (delta)

## ADDED Requirements

### Requirement: Upstream-сравнение по наборам

Единая форк-страница `docs/fork.html` SHALL показывать upstream-строки для каждого набора
(Shot List, Light, Medium) отдельной группой `Upstream comparison`, отделённой от наших
строк групповой строкой (не колонкой). Источники upstream: README Shot-List таблица
(наши харнессы исключены), `docs/leaderboard-results.json` (`light`, `medium`).

#### Scenario: Upstream-группа присутствует

- **WHEN** активен таб Shot List / Light / Medium
- **THEN** под нашими строками SHALL присутствовать группа `Upstream comparison`
  с upstream-строками этого набора (где источник доступен)

#### Scenario: Наши и upstream не смешиваются

- **WHEN** таблица отображается
- **THEN** наши строки SHALL идти в группе `Our runs`, upstream — в отдельной группе,
  без отдельной колонки-дискриминатора

#### Scenario: Upstream-строка в схеме

- **WHEN** показывается upstream-строка
- **THEN** она SHALL следовать той же схеме из девяти колонок; `Version` SHALL содержать
  `source_version`, либо `—` при отсутствии
