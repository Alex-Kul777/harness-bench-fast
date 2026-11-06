# add-fork-fail-output — proposal

## Why

На странице детализации прогона (`docs/fork-run-<id>.html`) упавшие задачи сейчас
показывают только **обрезанный сырой JSON** верификатора в колонке `Note` — читать
невозможно, причины и вывод не видны. Owner попросил оформить вывод упавших задач.

## What Changes

- Генератор `scripts/build_fork_pages.py` читает из per-task записи также поле `error`.
- В Tasks-таблице страницы детализации колонка `Note` становится **читаемой**:
  - короткий **reason** (ошибка, либо `reason`/ключевые поля верификатора, либо текст),
  - раскрывающийся `<details>` с **pretty-printed JSON** верификатора и `error` (если есть).
- Всё динамическое — через `html.escape`.

Не **BREAKING**: структура секций/колонок та же; меняется содержимое `Note`.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `result-reporting` — требование «Страница детализации прогона»
  дополняется выводом упавших задач.

## Out of scope

- Diff изменённых файлов (нет данных; правка раннера).
- Ссылки на ndjson-трейсы (отдельное решение по публикации/размеру).
- Основная страница `fork-medium90.html`.

## Impact

- `scripts/build_fork_pages.py`, `docs/fork-run-<id>.html` (генерируются).
- OpenSpec `specs/result-reporting/spec.md` (delta).

## Tracking

- Workboard: `7e34ac45` (board project-a)
- Epic: #431
