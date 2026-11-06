# result-reporting (delta)

## ADDED Requirements

### Requirement: Версионирование ассетов страницы

Ассеты опубликованной форк-страницы (`docs/fork-medium90.html`) SHALL подключаться с
query-версией (`…?v=<version>`), чтобы браузер не мог смешать устаревший закешированный
`fork-results.js` со свежей разметкой.

#### Scenario: Теги ассетов версионированы

- **WHEN** страница `docs/fork-medium90.html` публикуется
- **THEN** теги `<link>`/`<script>` SHALL содержать параметр `v`

#### Scenario: Обновление ассетов

- **WHEN** изменяется `docs/fork-results.js`
- **THEN** версия `v` в теге SHALL быть обновлена, чтобы клиенты получили новый файл
