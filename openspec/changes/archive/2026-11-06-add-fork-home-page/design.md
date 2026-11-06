# add-fork-home-page — design

## Решение
Одна статическая страница (без JS-табов) — надёжнее и достаточно: три секции с
`id="shotlist" / "light" / "medium"` и anchor-навигацией. (Вариант A «табы» — надстройка
над этим, добавляется позже без переделки данных.)

## Единая схема колонок
`Harness · Profile · Model · Result · % · Time · Steps · Tokens (cost) · Version · Source`
- `Version`: наши строки → `task_set_version` из JSON; upstream → `source_version`.
- `Source`: `ours` / `upstream` (ссылка на исходный JSON для наших строк).
- Пустое значение → `—`.

## Источники
| Suite | Наши | Upstream |
| --- | --- | --- |
| Shot List (52) | `results/*_shotlist*.json` (оба dir, dedup; исключая part2/rerun/smoke/sample/diag/pilot) | — (нет машинного источника) |
| Light (391) | allow-list: `results/{hermes,glm52,oc}_full_391.json` | `docs/leaderboard-results.json` rows with `light` |
| Medium (80) | `docs/fork-medium90-results.json` rows (агрегат long+reflect+feasibility) | — (в этой итерации) |

## Данные (`docs/fork-home-results.json`)
`{generated_by, id:"fork-home", version_semantics, suites:[{key,label,tasks,ours[],upstream[]}]}`

## Безопасность
Все динамические значения — `html.escape`. Ссылки — на `blob/main/<path>`.
