# add-medium-90-and-sample-tab — tasks

## 1. Генератор
- [x] 1.1 `build_fork_pages.py`: Medium = 90 (волна `composite_hard` 512–530); пустые волны не в sample
- [x] 1.2 `build_fork_home.py`: `ours_medium` → `X/Y (partial Y/90)`; upstream из `docs/medium90-results.json`
- [x] 1.3 Новый набор `medium-sample` (`#medium-sample`): охват + пилоты из манифеста
- [x] 1.4 `docs/fork-medium-pilot-manifest.json` (13 задач, bands)

## 2. Спека
- [x] 2.1 Delta `result-reporting`: MODIFIED «Единая форк-страница» + ADDED «Полный Medium» / «Урезанный семпл»

## 3. QA / верификация
- [x] 3.1 `build_fork_results.py --check` / `--lint` → 0; `build_fork_home.py --check` → 0; `build_fork_pages.py --check` → 0
- [x] 3.2 HTML: 4 таб-кнопки/панели; `#medium` ряд `55/66 (partial 66/90)`; `#medium-sample` ряды `66/90` + `13/90`
- [x] 3.3 `openspec validate --all --strict` → 0
- [x] 3.4 Live: `fork.html#medium` и `#medium-sample` 200, активны нужные табы; старые URL 200
