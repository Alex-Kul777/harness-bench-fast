# version-fork-page-assets — proposal

## Why

Пользователь увидел «съехавшие» колонки: под `Profile` стояло `3/3`, последняя колонка
пустая, harness — `Pi · 2 runs` (старый текст). Диагностика: сервер отдавал **новый**
`fork-results.js`, но браузер использовал **старый закешированный** скрипт, т.к. тег
`<script src="fork-results.js">` не был версионирован. HTML при этом перечитался новый →
новая шапка + старый рендер → сдвиг на одну колонку.

## What Changes

- Asset-теги страницы `docs/fork-medium90.html` версионируются:
  `landing.css?v=…` и `fork-results.js?v=…` (паттерн upstream: `landing.css?v=medium90-…`).
- Это не даёт браузеру смешать старый скрипт с новой шапкой.

Не **BREAKING**: данные/логика не меняются; меняется только URL ассетов.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `result-reporting` — добавляется требование о версионировании
  ассетов опубликованной форк-страницы.

## Out of scope

- Версионирование самого `docs/index.html`/`leaderboard.js` (upstream-файлы).
- Логика рендера и схема данных.

## Impact

- `docs/fork-medium90.html`.
- OpenSpec `specs/result-reporting/spec.md` (delta).

## Tracking

- Workboard: `TBD` (board project-a)
- Epic: #431
