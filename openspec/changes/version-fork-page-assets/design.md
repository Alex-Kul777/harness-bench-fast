# version-fork-page-assets — design

## Решение

Тег скрипта (и стилей) страницы получает query-версию:

```html
<link rel="stylesheet" href="landing.css?v=20261106-1">
<script src="fork-results.js?v=20261106-1" defer></script>
```

При правке ассетов версия инкрементируется (или берётся дата сборки). JSON-данные уже
защищены `fetch(..., {cache:"no-cache"})`, менять их не нужно.

## Почему не «no-store» на скрипт

Скрипт — статический ассет; версионирование URL — идиома upstream и не отключает
кэш целиком (быстрее для пользователя), но гарантирует свежую пару «шапка+рендер».

## Верификация

- Live-страница отдаёт теги с `?v=`.
- При «свежем» браузере таблица совпадает: `Profile | Long | Reflect | Feasibility | Overall | 95% interval | Steps | Tokens (cost)`.
