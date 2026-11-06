# add-fork-page-canonical-columns — proposal

## Why

Форк-страница результатов (`docs/fork-medium90.html`) отклонилась от канонического набора
колонок форка. Owner проверяет каждую форк-таблицу на полный набор и уже отметил пропажу двух:

1. **Нет стоимости в ₽.** Данные её содержат (`usage.cost_rub`), но страница рендерит только
   сырые токены (`Tokens`), без `Tokens (cost)`. Причина — страница копировала колонки
   upstream (`Steps | Tokens`), а не канонические колонки форка.
2. **Нет столбца `Profile`.** Поле `profile` в данных есть, но отдельной колонки в шапке нет —
   профиль прятался в подписи harness.

## What Changes

- В per-config таблице страницы добавляется колонка **`Profile`** (`—`, если не задан) и
  колонка **`Tokens (cost)`** (слитые токены + ₽, как в канонических таблицах форка).
- Форматирование: `formatCost` (₽, группировка пробелом) и `tokensCostCell`.
- Заголовки `<thead>` в HTML и рендер в `docs/fork-results.js` синхронизируются.

Не **BREAKING**: волны/матрица/Wilson не меняются; добавляются две колонки.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `result-reporting` — требование «Страница-таблица результатов
  форка» расширяется каноническими колонками `Profile` и `Tokens (cost)`.

## Out of scope

- Изменение генератора данных (поля `profile` и `usage.cost_rub` уже присутствуют).
- Пересчёт методологии/Wilson.
- Матрица Harness × Wave (колонки-волны, канонический набор к ней не применяется).

## Impact

- `docs/fork-medium90.html`, `docs/fork-results.js`.
- OpenSpec `specs/result-reporting/spec.md` (delta).

## Tracking

- Workboard: `b2245723` (board project-a)
- Epic: #431
