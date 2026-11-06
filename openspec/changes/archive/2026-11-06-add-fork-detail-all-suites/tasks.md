# add-fork-detail-all-suites — tasks

- [x] 1.1 `_from_summary_file`: `detail`/`suite` + сбор `_DETAIL_JOBS`
- [x] 1.2 Shot List/Light: `detail=fork-detail-<stem>.html`
- [x] 1.3 `render_detail` (сводка + таблица задач) и запись в `main()`
- [x] 2.1 Delta `result-reporting`: ADDED «Детализация для всех наших наборов»
- [x] 3.1 Генерация: 15 `fork-detail-*.html`; `--check` → 0; ссылок = 16
- [x] 3.2 Коллизия: `build_fork_pages.py` не удаляет `fork-detail-*`
- [x] 3.3 `openspec validate --all --strict` → 0
- [x] 3.4 Live: `fork.html` 200; `fork-detail-*.html` 200; клик открывает детализацию
