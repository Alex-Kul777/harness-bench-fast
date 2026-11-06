# add-fork-results-pages — design

## Контекст

Upstream публикует результаты как **статический сайт** в `docs/`: `index.html` +
`landing.css` + `leaderboard.js`, который тянет `leaderboard-results.json` /
`medium90-results.json` и рисует таблицу колонок
`# | Model / harness | Passed | Score | Steps | Tokens`; отдельная `harness-wave19.html`
показывает матрицу **Harness × Model** и per-config таблицу с 95% Wilson.

Форк уже имеет markdown-слой (`FORK.md`, `docs/fork-results.md`, автоген
`scripts/build_fork_results.py`). Не хватает **страницы + данных**.

## Решения

1. **Данные — отдельный JSON, страница его только рендерит.** Так же, как upstream:
   источник правды — артефакты прогонов; HTML/JS ничего не считает, кроме форматирования.
2. **95% Wilson считается в генераторе** и кладётся в JSON (per-config, per-wave), чтобы
   страницу можно было проверить без запуска JS и не дублировать формулу.
3. **Umbrella-suite «Medium (392–471)»** в `build_fork_results.py`: long 20 + reflection 20
   + feasibility 40 — один знаменатель, как требует скилл fork-doc-layering (sub-waves не
   должны расползаться по сюжетам без общего total).
4. **Имена файлов**: `docs/fork-medium90-results.json`, `docs/fork-medium90.html`,
   `docs/fork-results.js` (не трогаем upstream `index.html`/`leaderboard.js`/`landing.css`,
   только переиспользуем `landing.css` через `<link>`).
5. **Pages**: включаем на `main` / `/docs` (репо уже хранит сайт в `docs/`).

## Замороженная схема `docs/fork-medium90-results.json`

```jsonc
{
  "generated_by": "scripts/build_fork_pages.py",
  "task_set_version": "v0.21.3",
  "medium_tasks": 80,
  "provenance": "свободный текст: откуда данные, k=1, инфра-сбоев нет",
  "waves": [
    { "key": "long",        "label": "Long context",   "task_range": "392–411", "tasks": 20 },
    { "key": "reflect",     "label": "Tool reflection","task_range": "412–431", "tasks": 20 },
    { "key": "feasibility", "label": "Feasibility",    "task_range": "432–471", "tasks": 40 }
  ],
  "rows": [
    {
      "id": "pi-deepseek-v41flash",
      "harness": "Pi",
      "model": "DeepSeek-V4.1-Flash",
      "profile": null,                     // "thinking: off" | "MCP off" | null
      "runs": 1,
      "suites": {                          // key ∈ waves[].key, иначе отсутствует
        "long":        { "passed": 3, "total": 3, "measurement": "partial" },
        "reflect":     null,               // null = не измерено (не «провал»)
        "feasibility": { "passed": 1, "total": 1, "measurement": "partial" }
      },
      "usage": { "seconds": 7392.7, "steps": 1321, "tokens": 62239572, "cost_rub": 3298.6 },
      "wilson": {                          // 95% Wilson для каждого непустого suite
        "long": [0.438, 1.0],
        "feasibility": [0.207, 1.0]
      },
      "sources": ["pi_pilot_long3_20261105.json", "wave19_smoke_432.json"]
    }
  ]
}
```

Правила:
- `measurement`: `"partial"`, если `total` < ожидаемого числа задач волны, иначе `"complete"`.
- `suites[key] === null` ⇒ в таблице «Unmeasured», **не** 0/N.
- `wilson[key]` — `[lo, hi]` в долях (0..1), округление до 3 знаков.
- Строки без `summary` игнорируются. Имена с `smoke/sample/diag/part2/rerun`
  **исключаются** как непубликуемые; `pilot` сохраняется и помечается `partial`.
- Строка без резолвимого `harness`/`model` **не попадает** в данные (никаких «unknown»-рядов);
  для известных артефактов волн без токена в имени (`pi_pilot_long3`, `wave19_full_ds41flash`)
  harness/model задаются явной картой `RUN_META_OVERRIDES` в генераторе.

## Формула Wilson (95%, z = 1.96)

```
center = (p + z²/2n) / (1 + z²/n)
half   = z/√n * √( p(1−p)/n + z²/4n² ) / (1 + z²/n)
lo = max(0, center − half); hi = min(1, center + half)
```

## Структура страницы `docs/fork-medium90.html`

- `<header>`: бренд `harness_bench_fast.` → `index.html`; ссылка на `FORK.md`.
- Suite-switch: `Medium 80 (392–471)` (по умолчанию) — как у upstream кнопки Light/Medium.
- Таблица 1 — **матрица Harness × Wave**: строки = harness, столбцы = long/reflect/feasibility,
  ячейка = `passed/total (pct%)` или `—`.
- Таблица 2 — **per-config**: `# | Model / harness | Long | Reflect | Feasibility | Overall | 95% interval | Steps | Tokens`.
- Search по модели/harness; `#empty` при пустом фильтре.
- Fine-print: «No LLM judge…», пометка partial/unmeasured.

## Риски

- Расхождение схемы между генератором и страницей → схема **заморожена здесь**, оба артефакта
  пишутся под неё; проверка — локальный рендер + сверка счётчиков с `results/*.json`.
- Pages затрёт upstream-лендинг? Нет: форк публикует свой `docs/` (в форке свой upstream merge-guard).
