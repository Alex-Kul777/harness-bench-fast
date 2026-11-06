# add-fork-page-canonical-columns — design

## Решение

Per-config таблица страницы получает канонические форк-колонки, сохраняя уже существующие
per-wave колонки как «extras»:

```
# | Model / harness | Profile | Long | Reflect | Feasibility | Overall | 95% interval | Steps | Tokens (cost)
```

- `Profile` — из `row.profile`; `—`, если `null` (в подписи harness профиль больше не дублируется).
- `Tokens (cost)` — `compact(tokens) + " (" + formatCost(cost_rub) + ")"`, напр. `110.4M (7 189₽)`;
  при отсутствии cost — только токены; `formatCost` группирует пробелом и добавляет `₽`.

## Совместимость

- Данные/схема не меняются: генератор уже пишет `profile` и `usage.cost_rub`.
- Матрица Harness × Wave не трогается (её колонки — волны).
- Wilson-интервал остаётся отдельной колонкой (non-canonical extra, как разрешает скилл fork-doc-layering).

## Верификация

- Node-рендер реального JSON показывает колонку `Profile` и `Tokens (cost)` c `₽`.
- Страница на Pages отдаётся 200 и содержит новые заголовки.
