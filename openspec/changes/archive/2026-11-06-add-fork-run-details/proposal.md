# add-fork-run-details — proposal

## Why

1. Owner попросил, чтобы **строка per-config таблицы вела в детализацию прогона**: клик по
   `Model / harness` → страница с деталями (волны, задачи, источники).
2. В таблице **нет колонки `Time`** (длительность), хотя это каноническая колонка форка —
   данные её содержат (`usage.seconds`), страница не рендерит.

## What Changes

- Генератор `scripts/build_fork_pages.py`:
  - добавляет в строку JSON поле **`details_url`** (`fork-run-<id>.html`);
  - собирает per-task записи из `results[]` прогонов;
  - генерирует статическую страницу детализации **`docs/fork-run-<id>.html`** на каждую
    конфигурацию (волны, задачи, источники).
- Страница `docs/fork-medium90.html` / `docs/fork-results.js`:
  - новая колонка **`Time`** (минуты из `usage.seconds`);
  - ячейка `Model / harness` становится ссылкой на `details_url`;
  - версия ассетов инкрементируется.

Не **BREAKING**: поля волн/Wilson прежние; добавляется колонка и ссылка.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `result-reporting` — страница-таблица получает колонку `Time`
  и ссылку на детализацию; добавляется требование о странице детализации прогона.

## Out of scope

- Пер-задачная БД/бэкенд: детализация — статический HTML из уже сохранённых JSON.
- Изменение методики/Wilson.

## Impact

- `scripts/build_fork_pages.py`, `docs/fork-medium90.html`, `docs/fork-results.js`,
  `docs/fork-run-<id>.html` (генерируются).
- OpenSpec `specs/result-reporting/spec.md` (delta).

## Tracking

- Workboard: `48a0a1f9` (board project-a)
- Epic: #431
