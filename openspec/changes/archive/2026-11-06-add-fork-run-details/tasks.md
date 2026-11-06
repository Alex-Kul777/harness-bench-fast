# add-fork-run-details — tasks

## 1. Генератор (scripts/build_fork_pages.py)

- [x] 1.1 Добавить в строку JSON поле `details_url` (`fork-run-<id>.html`)
- [x] 1.2 Собирать per-task записи из `results[]` (task_id, passed, message, elapsed_seconds, agent_steps, agent_total_tokens); маппить в волну по диапазону task_id
- [x] 1.3 Генерировать `docs/fork-run-<id>.html` (waves/tasks/sources; HTML-экранирование)
- [x] 1.4 `--check` продолжает проверять JSON; генерация страниц — при записи

## 2. Страница результатов

- [x] 2.1 `docs/fork-medium90.html`: добавить колонку `Time`; инкремент версии ассетов
- [x] 2.2 `docs/fork-results.js`: `formatDuration`; рендер `Time`; ячейка `Model / harness` — ссылка на `details_url`

## 3. Спека

- [x] 3.1 Delta `result-reporting`: MODIFIED страница-таблица (Time + ссылка); ADDED страница детализации

## 4. QA / верификация

- [x] 4.1 Генератор создаёт JSON + `fork-run-<id>.html`; `--check` → 0
- [x] 4.2 Node-рендер: `Time` присутствует, ссылка ведёт на существующий файл
- [x] 4.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [x] 4.4 Live: строка ведёт на детализацию (HTTP 200)
