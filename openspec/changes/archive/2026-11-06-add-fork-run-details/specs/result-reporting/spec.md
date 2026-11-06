# result-reporting (delta)

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
  из `row.usage.cost_rub`; при отсутствии стоимости SHALL показываться только токены

#### Scenario: Колонка Time

- **WHEN** per-config таблица отрисовывается
- **THEN** колонка `Time` SHALL показывать длительность прогона в минутах из
  `row.usage.seconds` (`—` при отсутствии)

#### Scenario: Ссылка на детализацию

- **WHEN** у строки задан `details_url`
- **THEN** ячейка `Model / harness` SHALL быть ссылкой на соответствующую страницу
  детализации прогона

## ADDED Requirements

### Requirement: Страница детализации прогона

Генератор `scripts/build_fork_pages.py` SHALL создавать для каждой конфигурации
статическую страницу `docs/fork-run-<id>.html` с разбивкой по волнам, списком задач
(при наличии per-task записей) и источниками прогонов.

#### Scenario: Генерация детализации

- **WHEN** запускается `python3 scripts/build_fork_pages.py`
- **THEN** по каждой строке SHALL создаваться `docs/fork-run-<id>.html`, а в JSON
  появляться поле `details_url`

#### Scenario: Источники экранированы

- **WHEN** страница детализации рендерит имена источников и сообщения задач
- **THEN** текст SHALL быть HTML-экранирован
