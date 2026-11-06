# result-reporting (delta)

## ADDED Requirements

### Requirement: Данные о длительности прогона

Генератор форк-страницы SHALL агрегировать per-task `elapsed_seconds` из наших
прогонов и из апстрим-замеров
(`docs/{codex-deepseek,miniswe-deepseek,claudecode-sonnet}-medium90-*.json`) и SHALL
записывать `rows[].suites[<wave>].duration = {n,mean,median,max}` и top-level
`duration_by_wave` (наши + три апстрим-конфигурации, секунды).

#### Scenario: Джойн по задачам

- **WHEN** запускается `python3 scripts/build_fork_pages.py`
- **THEN** JSON SHALL содержать по каждой измеренной волне mean/median/max секунд
  для `Pi (ours)` и для доступных апстрим-конфигураций

#### Scenario: Нет данных по конфигурации

- **WHEN** у конфигурации нет per-task времени для волны
- **THEN** она SHALL отсутствовать в списке этой волны (а SHALL NOT показываться как 0)

### Requirement: Колонка Duration на странице

Страница `docs/fork-medium90.html` SHALL показывать колонку `Duration` в таблице
per-config и таблицу `Duration by wave` (строки — конфигурации, столбцы — волны).

#### Scenario: Отрисовка длительности

- **WHEN** страница открывается
- **THEN** ячейки SHALL показывать секунды (mean с `n`) или `—`, и текст SHALL быть
  экранирован
