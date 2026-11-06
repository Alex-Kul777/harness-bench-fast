# add-fork-upstream-rows — design

## Источники upstream по наборам
| Suite | Источник | Кол-во |
| --- | --- | --- |
| Shot List (52) | `README.md` → «## Shot List Leaderboard (52 tasks)» markdown-таблица; строки с харнессом ∉ {Pi, OpenClaw, Hermes} | 10 |
| Light (391) | `docs/leaderboard-results.json` rows с `light` | 96 |
| Medium (80) | `docs/leaderboard-results.json` rows с `medium` | 22 |

## Правила
- `ours` и `upstream` разделяются групповыми строками (`tr.group`), не колонкой.
- Прочерки в README нормализуются (`-`/`–` → `—`); тысячные запятые → пробелы.
- `Version` upstream: `source_version` (Light/Medium) или `—` (Shot List — в README нет).

## Безопасность
Все значения — `html.escape`.
