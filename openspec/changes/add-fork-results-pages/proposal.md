# add-fork-results-pages — proposal

## Why

Наши прогоны новых волн (long 392–411, reflect 412–431, feasibility 432–471) сейчас
видны только в чате/issue и частично в markdown. Owner читает **опубликованный сайт**
(как upstream `ai-forever.github.io/harness-bench-fast`), поэтому волна, живущая
только в markdown, остаётся невидимой. Нужна форк-страница результатов и данные к ней.

## What Changes

- Новый генератор `scripts/build_fork_pages.py`: сканирует `results/` (checkout + родитель),
  сводит прогоны по **волнам** (long/reflect/feasibility = umbrella-suite «Medium 392–471»),
  считает `{passed,total}`, usage и 95% Wilson, пишет `docs/fork-medium90-results.json`.
- Новая страница `docs/fork-medium90.html` (+ `docs/fork-results.js`): матрица
  **Harness × Wave** и per-config таблица с 95% Wilson, suite-switch + search. Молча
  копирует порядок колонок и формулировки upstream-лендинга и `harness-wave19.html`.
- `scripts/build_fork_results.py`: регистрируется umbrella-suite **Medium (392–471)**
  (long 20 + reflection 20 + feasibility 40), чтобы новые волны попадали в авто-блок.
- GitHub Pages форка включается на ветке `main`, каталог `/docs`.

Не **BREAKING**: `--check`/`--lint`/авто-блок сохраняют поведение; добавляется новый сюжет.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `result-reporting` — добавляются требования о данных
  страницы, самой странице, публикации через Pages и реестре волн (delta-спека).

## Out of scope

- Сами полные прогоны волн (отдельный go/no-go) — страница заполняется по мере появления JSON.
- Правка upstream README и методологии бенчмарка.
- Замена `docs/fork-results.md` (он остаётся; страница — дополнительная поверхность).

## Impact

- `scripts/build_fork_pages.py` (новый), `scripts/build_fork_results.py` (регистрация suite),
  `docs/fork-medium90.html`, `docs/fork-results.js`, `docs/fork-medium90-results.json` (генерится).
- `.github/workflows/*` — при необходимости шаг `build_fork_pages.py --check`.
- Данные/upstream-слой не затрагиваются.

## Tracking

- Workboard: `b7b5f134` (board project-a)
- Epic: #431
