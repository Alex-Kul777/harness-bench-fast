# add-fork-home-tabs — tasks

## 1. Генератор
- [x] 1.1 Табы: `.suite-switch` + `data-suite-panel` + inline-JS (hash-aware)
- [x] 1.2 Ровно 9 колонок; `ours`/`upstream` — групповые строки
- [x] 1.3 Medium `waves` → `<details>` под таблицей

## 2. Спека
- [x] 2.1 Delta `result-reporting`: MODIFIED «Единая форк-страница» (табы + 9 колонок)

## 3. QA / верификация
- [x] 3.1 Генерация; `--check` → 0
- [x] 3.2 HTML: 3 таб-кнопки, 3 панели, 9 `<th>`, `waves` details
- [x] 3.3 `openspec validate --all --strict` → 0
- [x] 3.4 Live: `fork.html` 200; `fork.html#light`/`#medium` активируют таб; старые URL 200
