# add-fork-page-canonical-columns — tasks

## 1. Правка страницы

- [x] 1.1 `docs/fork-medium90.html`: в шапке per-config таблицы добавить `<th>Profile</th>` и переименовать `Tokens` → `Tokens (cost)`
- [x] 1.2 `docs/fork-results.js`: добавить `formatCost` (₽) и `tokensCostCell`; рендерить колонку `Profile`; убрать дублирование профиля в подписи harness
- [x] 1.3 Экспортировать новые функции под `module.exports`

## 2. Спека

- [x] 2.1 Delta `result-reporting`: MODIFIED «Страница-таблица результатов форка» — обязательные колонки `Profile` и `Tokens (cost)`

## 3. QA / верификация

- [x] 3.1 Node-рендер: колонки `Profile` и `Tokens (cost)` присутствуют; `₽` в ячейке
- [x] 3.2 `node --check docs/fork-results.js` → ok
- [x] 3.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [x] 3.4 После пуша: страница на Pages отдаётся 200 и содержит новые заголовки
