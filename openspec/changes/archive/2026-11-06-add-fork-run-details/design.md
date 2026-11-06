# add-fork-run-details — design

## Замороженные интерфейсы

### JSON (аддитивно к `docs/fork-medium90-results.json`)
Каждая строка доп. поле:
- `details_url`: строка, напр. `"fork-run-pi-deepseek-v4-1-flash.html"`.

Схема волн/`suites`/`usage`/`wilson`/`sources` — без изменений.

### Страница детализации `docs/fork-run-<id>.html` (генерируется генератором)
- Статическая (данные «впечатаны»); переиспользует `landing.css`.
- `<header>`: бренд → `index.html`; ссылка назад → `fork-medium90.html`.
- H1: `«{model} — {harness}»` (+ `profile`, если есть); подпись: число прогонов.
- Таблица **Waves**: `Wave | Tasks | Passed | % | 95% Wilson | Time | Steps | Tokens (cost)`.
- Таблица **Tasks** (если есть per-task записи): `Task | Wave | Result | Time (s) | Steps | Tokens | Note`.
  - `Result` = `pass`/`fail` (по `passed`), Note = усечённое `message` (экранировать!).
- Секция **Sources**: список имён файлов прогонов; при возможности ссылка на
  `https://github.com/Alex-Kul777/harness-bench-fast/blob/main/results/<name>`.
- Fine-print.

### Маппинг волн по `task_id`
`392–411` → long; `412–431` → reflect; `432–471` → feasibility. Иначе — пропустить.

### Page `docs/fork-medium90.html` (per-config)
Порядок колонок:
`# | Model / harness | Profile | Long | Reflect | Feasibility | Overall | 95% interval | Time | Steps | Tokens (cost)`
- `Time` = `(usage.seconds / 60).toFixed(1) + "m"` (напр. `297.3m`); `—` если нет.
- `Model / harness`: если `row.details_url` задан — обернуть в `<a href="{details_url}">`.
- Asset-версии: `?v=20261106-2`.

## Верификация

- `python3 scripts/build_fork_pages.py` создаёт JSON + `docs/fork-run-<id>.html`.
- Node-рендер: в шапке есть `Time`; ссылка ведёт на `fork-run-*.html`; файл существует.
- Live: клик по строке открывает детализацию (200).
