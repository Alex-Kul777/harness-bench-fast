# add-fork-light-page — design

## Источники (наши Light-прогоны)
Явный allow-list (не скан), т.к. `results/glm52_full_391.json` не имеет harness-префикса:

| Harness | Profile | Model | Файл (RESULT_DIRS: `results/` → `../results/`) |
| --- | --- | --- | --- |
| Hermes | MCP off | GLM-5.2 | `results/hermes_full_391.json` |
| Pi | high | GLM-5.2 | `results/glm52_full_391.json` |
| OpenClaw | — | GLM-5.2 | `results/oc_full_391.json` |

Правило форка: сырые прогоны — `runs/*_v016.json`; **актуальная сводка берётся из `results/`**.
Поэтому Pi = `results/glm52_full_391.json` (385/391), а не raw `runs/pi_glm52_high_full391_v016.json`.

Чтение: `summary` (если есть) предпочтительно; иначе top-level `passed/total/pass_rate/steps/tokens`.
Время = `total_seconds/60`. Стоимость = `estimated_cost_rub` (иначе `—`).

## Upstream-строки (сравнение)
`docs/leaderboard-results.json` → `rows[]`, у которых есть `light` (96 шт). Поля:
`harness`, `model`, `light{passed,total}`, `source_version`. Сортировка по `passed` desc.

## Схема данных (`docs/fork-light-results.json`)
```
{
  "generated_by": "scripts/build_fork_light.py",
  "id": "fork-light",
  "suite": {"key": "light", "label": "Light (391)", "tasks": 391},
  "config": {"harness": "Pi", "model": "GLM-5.2"},
  "ours": [{harness, profile, model, passed, total, pass_rate, minutes, steps, tokens, cost_rub, source}],
  "upstream": [{harness, model, passed, total, source_version}]
}
```

## Безопасность
Все динамические значения — через `html.escape` (или `textContent` в JS). Ссылки на JSON —
на `blob/main/<path>` GitHub.
