# add-fork-home-tabs

## Why
Единая форк-страница `docs/fork.html` сейчас показывает три набора подряд (стек).
Владелец выбрал **вариант A**: переключение табами (Shot List / Light / Medium),
ровно девять канонических колонок, волновая разбивка Medium — в раскрывающемся блоке.

## What Changes
- `scripts/build_fork_home.py` → `docs/fork.html` становится таб-страницей: свитчер
  `suite-switch` + inline-JS; видна одна секция за раз; состояние следует URL-hash
  (`#shotlist` / `#light` / `#medium`), поэтому старые редиректы продолжают работать.
- Таблицы содержат **ровно 9 колонок** `Harness · Profile · Model · Result · % · Time ·
  Steps · Tokens (cost) · Version`; `ours`/`upstream` разделены групповыми строками (не колонкой).
- Волновая разбивка Medium (long/reflect/feasibility) — в блоке `<details>` под таблицей.

## Impact
- Только `docs/fork.html` (+ существующий JSON). Прогоны не меняются.
- Данные: `docs/fork-home-results.json` — без изменений схемы (добавлено поле `waves` для Medium).
