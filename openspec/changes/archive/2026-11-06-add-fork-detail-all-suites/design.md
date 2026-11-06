# add-fork-detail-all-suites — design

## Кто генерирует детализацию
- **Medium**: `scripts/build_fork_pages.py` → `docs/fork-run-<id>.html` (не трогаем).
- **Shot List / Light**: `scripts/build_fork_home.py` → `docs/fork-detail-<stem>.html`.

## Почему префикс `fork-detail-`
`build_fork_pages.py::write_pages` удаляет «лишние» `docs/fork-run-*.html` (glob по своему
набору). Отдельный префикс исключает случайное удаление наших новых страниц (проверено).

## Страница детализации
- Заголовок `Harness · Model`, мета: Profile / Version / Result (% / Time / Steps / Tokens (cost)).
- Таблица задач из `tasks`/`results` JSON: `task_id`, PASS/FAIL, секунды, токены, сообщение
  (короткое — inline, длинное — в `<details>`).
- Обратная ссылка на `fork.html#<suite>`.
- Всё динамическое — `html.escape`.

## Данные
`_DETAIL_JOBS` собирается в `_from_summary_file(... detail=...)` и пишется в `main()` (не в `--check`).
