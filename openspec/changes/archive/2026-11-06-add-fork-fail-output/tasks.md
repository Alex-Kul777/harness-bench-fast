# add-fork-fail-output — tasks

## 1. Генератор

- [x] 1.1 Читать `error` в per-task записи
- [x] 1.2 Реализовать `task_reason(message, error)` (unwrap `{"wave19": …}`, reason/ключевые поля, иначе текст)
- [x] 1.3 В Tasks-таблице: `Note` = reason; для fail/структурированных сообщений — `<details>` с pretty JSON + error
- [x] 1.4 Короткий `<style>` для `.task-detail pre`; всё экранировать

## 2. Спека

- [x] 2.1 Delta `result-reporting`: MODIFIED «Страница детализации прогона» + сценарии вывода упавших задач

## 3. QA / верификация

- [x] 3.1 Регенерация: `task-detail` присутствует; `task_456` показывает причину
- [x] 3.2 Инъекция `<script>` в message → экранировано
- [x] 3.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [x] 3.4 Live: детализация 200, fail-строка с раскрывающимся выводом
