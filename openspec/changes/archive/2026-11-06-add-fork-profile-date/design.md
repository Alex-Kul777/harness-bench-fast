# add-fork-profile-date — design

## Резолвер даты (наши строки)
`date = session_id(JSON) or имя_файла(_YYYYMMDD) or README_shotlist[(harness,model,profile)]`

| Набор | Рабочий источник | Покрытие |
| --- | --- | --- |
| Shot List (52) | README Shot-List (наши строки, дата в скобках) | ~11/12 |
| Light (391) | `session_id` (Hermes) | 1/3 |
| Medium (80) | имя файла-источника `_YYYYMMDD` | 1/1 |

## Upstream
`measurement_date` из `docs/leaderboard-results.json` (Medium — есть; Light — часто нет).
Shot List upstream — дата уже в README-ячейке Profile.

## Формат
`_with_date(profile, date)` → `f"{profile or '—'} ({date})"`; без даты — как есть.
Отсутствие даты — честный прочерк, не выдумываем.

## Ограничение (документируем)
У большинства наших артефактов прогона нет поля даты; источники выше — прокси.
Стратегическое решение — писать дату в JSON раннером (отдельная задача).
