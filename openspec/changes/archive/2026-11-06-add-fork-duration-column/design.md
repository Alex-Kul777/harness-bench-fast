# add-fork-duration-column — design

## Sources of per-task time

- **Ours:** each scanned run file has a top-level `results[]` list; a task record
  carries `elapsed_seconds` (seconds) and `task_id` (e.g. `results/wave19_full_ds41flash.json`).
- **Upstream:** `docs/codex-deepseek-medium90-20261027.json`,
  `docs/miniswe-deepseek-medium90-20261027.json`,
  `docs/claudecode-sonnet-medium90-20261027.json` → `outcomes[]` with
  `{number, elapsed_seconds}` (tasks 392–471).

## Frozen schema additions (additive, v2)

```jsonc
// inside rows[] → suites[<wave>]
"duration": { "n": 3, "mean": 2449.8, "median": 2174.5, "max": 3571.2 }   // seconds, 1 dp

// new top-level key
"duration_by_wave": {
  "long": [
    { "label": "Pi (ours)",            "n": 3,  "mean": 2449.8, "median": 2174.5, "max": 3571.2 },
    { "label": "Codex + DeepSeek",     "n": 20, "mean": 1127.0, "median": 992.0,  "max": 3237.0 },
    { "label": "mini-SWE + DeepSeek",  "n": 20, "mean": 1837.0, "median": 1542.0, "max": 4594.0 },
    { "label": "Claude Code + Sonnet", "n": 20, "mean": 417.0,  "median": 21.0,   "max": 3391.0 }
  ],
  "reflect": [ /* same shape */ ],
  "feasibility": [ /* same shape */ ]
}
```

Rules:
- `mean`/`median`/`max` are seconds, rounded to 1 dp; `n` = number of tasks with a
  non-null `elapsed_seconds`.
- A wave with no data for a config is omitted from that wave's list (never 0).
- `Pi (ours)` is aggregated across **all** our wave-matched runs (existing runs +
  any sample files the scanner includes); label stays `Pi (ours)`.

## Page

- **Per-config table:** add a `Duration` column = our mean seconds/task across the
  measured waves, rendered compact (`2,450s`) or `—`.
- **New table `Duration by wave`:** rows = configuration label, columns =
  `Long / Reflect / Feasibility`, cell = `mean s (n=..)`; `—` when absent.
- Keep the existing `Steps`/`Tokens`/95% interval columns and all wording.

## Risks

- Our per-task time covers only a subset (long pilot 3–4, reflect sample, feasibility
  40) → `n` is shown so the reader sees the denominator.
- Upstream files are frozen snapshots; we only read them.
- Rounding/units: seconds everywhere; the page may also show minutes in a header note.
