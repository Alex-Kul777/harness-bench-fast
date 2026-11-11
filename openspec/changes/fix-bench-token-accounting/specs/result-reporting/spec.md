## MODIFIED Requirements

### Requirement: Страница-таблица результатов форка

Форк SHALL предоставлять статическую страницу `docs/fork-medium90.html`, которая
рендерит данные из `docs/fork-medium90-results.json` и содержит матрицу
**Harness × Wave** и per-config таблицу с 95% Wilson-интервалом. Per-config таблица
SHALL содержать канонические колонки форка `Profile`, `Time` и `Tokens (cost)`, а
ячейка `Model / harness` SHALL быть ссылкой на страницу детализации прогона
(`details_url`).

#### Scenario: Отрисовка данных

- **WHEN** страница открывается в браузере
- **THEN** она SHALL отображать строки по конфигурациям и волнам, а неизмеренные волны
  помечать как `Unmeasured`, а не как `0/total`

#### Scenario: Колонка Profile

- **WHEN** per-config таблица отрисовывается
- **THEN** она SHALL содержать колонку `Profile` (`—`, если профиль не задан)

#### Scenario: Колонка Tokens (cost) в рублях

- **WHEN** per-config таблица отрисовывается
- **THEN** колонка `Tokens (cost)` SHALL показывать токены и оценку стоимости в рублях (`₽`)
  из `row.usage.cost_rub`, а стоимость SHALL включать cache-бакет прогона
  (`summary.estimated_cost_rub`), а SHALL NOT занижать её, отбрасывая cache

#### Scenario: Колонка Time

- **WHEN** per-config таблица отрисовывается
- **THEN** колонка `Time` SHALL показывать длительность прогона в минутах из
  `row.usage.seconds` (`—` при отсутствии)

#### Scenario: Ссылка на детализацию

- **WHEN** у строки задан `details_url`
- **THEN** ячейка `Model / harness` SHALL быть ссылкой на соответствующую страницу
  детализации прогона
