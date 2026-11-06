# add-fork-light-page — tasks

## 1. Генератор
- [x] 1.1 `scripts/build_fork_light.py`: читать 3 наших Light-JSON (allow-list, RESULT_DIRS)
- [x] 1.2 Читать upstream Light-строки из `docs/leaderboard-results.json`
- [x] 1.3 Писать `docs/fork-light-results.json` (схема из design.md)
- [x] 1.4 Генерировать `docs/fork-light.html` (канонические колонки, upstream-таблица, escape)

## 2. Интеграция
- [x] 2.1 Nav-ссылка `Light (391)` в `docs/fork-medium90.html`
- [x] 2.2 Nav-ссылка `Light (391)` в `docs/fork-sample.html`

## 3. Спека
- [x] 3.1 Delta `result-reporting`: ADDED «Light-вид форк-страниц»

## 4. QA / верификация
- [x] 4.1 Генерация → оба файла; `--check` → 0
- [x] 4.2 3 наших строки (385/387/378), upstream-строк ≥ 90
- [x] 4.3 `openspec validate --all --strict` → 0
- [x] 4.4 Live: `fork-light.html` 200 на GitHub Pages
