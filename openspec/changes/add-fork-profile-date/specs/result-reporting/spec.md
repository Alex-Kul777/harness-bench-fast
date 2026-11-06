# result-reporting (delta)

## ADDED Requirements

### Requirement: Дата прогона в колонке Profile

Страница `docs/fork.html` SHALL добавлять дату совершения бенчмарка к значению колонки
`Profile` в формате `профиль (YYYY-MM-DD)`. Дата SHALL определяться по доступным источникам
(`session_id` задач, имя файла `_YYYYMMDD`, курируемая README-таблица Shot List для наших
строк; `measurement_date` для upstream). При отсутствии даты колонка SHALL оставаться без
суффикса (дата не выдумывается).

#### Scenario: Дата добавлена

- **WHEN** для строки доступна дата прогона
- **THEN** `Profile` SHALL отображаться как `профиль (YYYY-MM-DD)` (напр. `thinking: off (2026-11-04)`)

#### Scenario: Дата недоступна

- **WHEN** для строки нет источника даты
- **THEN** `Profile` SHALL отображаться без суффикса даты (SHALL NOT выдумывать значение)

#### Scenario: Upstream-дата

- **WHEN** строка — upstream и имеет `measurement_date`
- **THEN** дата SHALL браться из `measurement_date`
