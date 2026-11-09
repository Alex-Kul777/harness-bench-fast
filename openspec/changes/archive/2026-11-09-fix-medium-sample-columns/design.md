# Design: fix-medium-sample-columns

## ADR-inline

**Решение:** привести `#medium-sample` к тем же преобразованиям метаданных, что уже
используются для `#medium`, — повторно используя существующие хелперы
`_with_date` / `_with_reasoning` / `_with_version` из `build_fork_home.py`, а не дублируя
логику в семпл-ветке.

### Дата (Profile)

`_with_date(profile, date)`. Источники даты (spec:332): `session_id` задач, имя файла
`_YYYYMMDD`, курируемая README-таблица; для пилота — дата манифеста / имени `sources`.
Нет источника → без суффикса (дата SHALL NOT выдумываться).

### Провайдер и уровень (Model)

`_with_reasoning(model, profile)` расширяется провайдером: `модель (cloud.ru) (уровень)`.
Провайдер наших строк — `cloud.ru` (Cloud.ru Foundation Models); upstream остаётся как есть
(`(OpenRouter)`). При неизвестном провайдере суффикс отсутствует.

### Версия (Harness)

`_with_version(harness, version)`. Версия берётся из артефакта прогона
(`harness_version` / `openclaw_version` / `cli_version` / `runner_version`); для этого
`build_fork_pages.py` добавляет `harness_version` в строки `docs/fork-medium90-results.json`.

### Steps

Колонка `Steps` заполняется из `usage.steps` строки medium90 (fallback —
`summary.total_steps` артефакта), иначе `—` (spec «Заполнение колонки Steps»).

### Почему не дублировать

Существующие хелперы уже покрыты поведением `#medium`; дублирование даст дрейф — как у
`"\u2014"`, который придётся вынести в single-source (`DASH`).

## Порядок применения (apply)

1. `fork_metadata.py`: `DASH` как единый источник.
2. `build_fork_pages.py`: пропагировать `harness_version` в строки medium90; использовать `DASH`.
3. `build_fork_home.py`: `sample_rows()` → `_with_date`/`_with_reasoning`(+провайдер)/`_with_version`;
   колонка `Steps` в `SAMPLE_HEAD`/`_sample_rows_html`; пилот Time/Tokens из манифеста; guard пустого манифеста.
4. `build_medium90_data.py`: `raise ValueError` + `try/except`; дедуп в `_fresh_medium90_row(...)`.
5. Тесты-сторожа; регенерация `docs/`; проверки.

## Тесты

`tests/test_fork_sample_columns.py`: дата / уровень+провайдер / версия / `Steps` присутствуют
в семпл-строках; пилот берёт Time/Tokens из манифеста; RU/EN паритет строк семпла.
