# add-fork-capability-sample-view — design

## Замороженные интерфейсы

### Манифест (уже создан)
`docs/fork-sample-manifest.json` — `{id, size, rule, waves:{long:[…],reflect:[…],feasibility:[…]}, tasks:[{number,task_id,wave,band,passed_by_configs}], notes, provenance}`.

### Источники результатов (allow-list)
```
SAMPLE_SOURCES = {
  "long":        ["pi_sample_long_20261106.json"],
  "reflect":     ["pi_sample_reflect_20261106.json", "pi_reflect_ds41flash_20261106.json"],
  "feasibility": ["wave19_full_ds41flash.json"],
}
```
Ищутся в `results/` (checkout, затем `../results/`). Для задачи берётся первая запись `results[]`
с её `task_id`. Нет записи → `passed=None`, `measured=false`.

### Валидность long
Все задачи волны `long` помечаются `invalid=true`, `invalid_reason="timeout 2400 < wave floor 7200"`.
Рендер: строка волны показывает `0/3 — invalid (timeout 2400 < floor 7200)`.

### `docs/fork-sample-results.json`
```
{
  "generated_by":"scripts/build_fork_pages.py",
  "id":"capability-sample-medium", "size":20,
  "config":{"harness":"Pi","model":"DeepSeek-V4.1-Flash"},
  "provenance":"…", "manifest":"fork-sample-manifest.json",
  "waves":[{"key":"long","label":"Long context","task_range":"392–411","tasks":3,"passed":0,"invalid":true,"invalid_reason":"…"}, …],
  "tasks":[{"number":392,"task_id":"…","wave":"long","band":"floor","passed":false,
            "elapsed_seconds":…,"agent_steps":…,"agent_total_tokens":…,"invalid":true,"note":"…"}]
}
```

### `docs/fork-sample.html` (статическая, генерируется)
- header: бренд → `index.html`; nav: «Fork results» → `fork-medium90.html`, «Manifest» → `fork-sample-manifest.json`.
- intro: 25% of Medium 80 (392–471), правило бэндов, ссылка на манифест/ADR.
- **Summary по волнам**: `Wave | Tasks | Passed | % | Band mix | Status` (long → status `invalid (timeout<floor)`).
- **Per-task**: `# | Task | Wave | Band | Result | Time (s) | Steps | Tokens | Note`
  (Note — переиспользовать `task_reason` + `<details>` для fail, как на детализации).
- provenance + ссылки на сырые JSON; fine-print. Всё экранировать (`html.escape`).

### Ссылка в Medium-виде
В `<nav>` `docs/fork-medium90.html` добавить `<a href="fork-sample.html">Capability sample (20)</a>`.

### CLI
`build_fork_pages.py` при записи дополнительно пишет `docs/fork-sample-results.json` и
`docs/fork-sample.html`; `--check` продолжает проверять только `fork-medium90-results.json`.

## Верификация
- Генерация создаёт оба файла; `--check` → 0.
- Node/HTML: страница содержит 20 задач, long-баннер `invalid`, feasibility 12 задач.
- Live: `fork-sample.html` 200.
