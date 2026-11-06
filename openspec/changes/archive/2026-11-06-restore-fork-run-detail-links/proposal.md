# restore-fork-run-detail-links

## Why
При переходе на единую `docs/fork.html` потерялась детализация прогонов: на
`fork-medium90.html` строки были кликабельны и открывали `fork-run-<id>.html`, а новая
страница на детализацию не ссылалась. Страницы детализации при этом живы (200).

## What Changes
- `scripts/build_fork_home.py`: строки с `details_url` (наши Medium-прогоны) снова
  кликабельны → страница `docs/fork-run-<id>.html`; харнесс-ячейка — `<a>`, вся строка
  кликабельна (`data-detail` + JS), курсор pointer.
- Строки без детализации — как прежде (не кликабельны).

## Impact
- Только `scripts/build_fork_home.py` + `docs/fork.html`. Детализация не меняется.
