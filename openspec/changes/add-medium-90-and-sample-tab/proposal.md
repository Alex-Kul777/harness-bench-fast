# add-medium-90-and-sample-tab

## Why
Апстрим-борд Medium — 90 задач (392–471 + wave 21 512–530), а форк-вкладка Medium
показывала только historical 80 без wave21 и без пометки неполного покрытия. Владелец
хочет: (1) полную вкладку **Medium (90)**, куда попадают наши прогоны, с видимой
пометкой «урезано»; (2) вторую вкладку **`#medium-sample`** — наш урезанный семпл
(суммарный охват + пилоты).

## What Changes
- `scripts/build_fork_pages.py`: Medium = **90** задач (добавлена волна `composite_hard`,
  512–530); пустые волны не попадают в capability-sample.
- `scripts/build_fork_home.py`: `ours_medium` показывает `X/Y (partial Y/90)`; новый
  набор `medium-sample` (`#medium-sample`) — наши урезанные наборы (охват + пилоты).
- Данные: `docs/medium90-results.json` (апстрим-90) — источник upstream-строк;
  `docs/fork-medium-pilot-manifest.json` — манифест пилота.
- Навигация: ссылки на `#medium` / `#medium-sample` в `FORK.md` и `docs/fork-results.md`.

## Impact
- Публичные `docs/` (`fork.html`, `fork-home-results.json`, `fork-medium90-results.json`,
  `fork-medium-pilot-manifest.json`) + два генератора. Прогоны не меняются.
- Существующие URL `fork-medium90.html` / `fork-light.html` продолжают редиректить.
