# add-fork-detail-all-suites

## Why
Drill-down (детализация прогона) был только у Medium-строк (страницы `fork-run-*.html`,
генерируемые `build_fork_pages.py`). Владелец хочет, чтобы **все наши строки** на
`docs/fork.html` (Shot List, Light, Medium) были кликабельны и вели на страницу прогона.

## What Changes
- `scripts/build_fork_home.py` генерирует страницы детализации для наших Shot List и Light
  прогонов: `docs/fork-detail-<stem>.html` (префикс `fork-detail-` во избежание коллизии с
  `fork-run-*` — последние `build_fork_pages.py` чистит по своему набору).
- Строки Shot List / Light получают `data-detail` → кликабельны (JS + `<a>`).
- Страница детализации: сводка (Profile/Version/Result/Time/Steps/Tokens) + таблица задач
  (результат, секунды, токены, сообщение с раскрытием).

## Impact
- `scripts/build_fork_home.py`, `docs/fork.html`, `docs/fork-detail-*.html`. Данные read-only.
- `build_fork_pages.py` не меняется (проверено: `fork-detail-*` не удаляются).
