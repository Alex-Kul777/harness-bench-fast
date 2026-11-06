# add-fork-home-page

## Why
Форк-результаты были размазаны по нескольким страницам (`fork-medium90.html`,
`fork-light.html`), а Shot List (52) вообще не имел страницы (только markdown).
Владелец хочет **одну** живую форк-страницу с Light, Medium и Shot List и единой
схемой колонок `Harness · Profile · Model · Result · % · Time · Steps · Tokens (cost) · Version`.

## What Changes
- Новый генератор `scripts/build_fork_home.py` → `docs/fork.html` + `docs/fork-home-results.json`.
- Страница `docs/fork.html`: три секции (Shot List 52 / Light 391 / Medium 80), у каждой —
  таблица в единой схеме (9 колонок + `Source`), наши строки + upstream-строки (Light).
  `Version` = task-set version (наши) / `source_version` (upstream).
- Старые URL `fork-medium90.html` и `fork-light.html` → редирект-заглушки на
  `fork.html#medium` / `fork.html#light` (ничего не ломается).
- Nav-ссылки на `fork.html` со страницы `fork-sample.html`.

## Impact
- Только `docs/` и `scripts/`. Прогоны не меняются; upstream-данные read-only.
