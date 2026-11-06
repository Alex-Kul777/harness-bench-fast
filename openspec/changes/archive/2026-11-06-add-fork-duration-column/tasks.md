# add-fork-duration-column — tasks

## 1. Данные (build_fork_pages.py)

- [x] 1.1 Collect per-task `elapsed_seconds` from our scanned run files (`results[]` records)
- [x] 1.2 Read `docs/{codex-deepseek,miniswe-deepseek,claudecode-sonnet}-medium90-*.json` → `outcomes[].{number,elapsed_seconds}`
- [x] 1.3 Write `rows[].suites[<wave>].duration = {n,mean,median,max}` and top-level `duration_by_wave` (Pi (ours) + 3 upstream) per design.md
- [x] 1.4 Keep the output deterministic; `--check` stays green; existing keys unchanged

## 2. Страница (docs/fork-medium90.html + docs/fork-results.js)

- [x] 2.1 Add a `Duration` column to the per-config table (our mean s/task across measured waves, compact or `—`)
- [x] 2.2 Add a `Duration by wave` table (rows = config label, cols = Long/Reflect/Feasibility, cell = `mean s (n=..)`)
- [x] 2.3 Read the new JSON keys; degrade to `—` when absent; escape text

## 3. QA / верификация

- [x] 3.1 `python3 scripts/build_fork_pages.py` then `--check` → 0
- [x] 3.2 node render: per-config rows show Duration; `duration_by_wave` has 3 waves × up to 4 configs
- [x] 3.3 spot-check: `Pi (ours)` long mean == mean of our long `elapsed_seconds`; Codex long mean ≈ 1127s
- [x] 3.4 `python3 scripts/build_fork_results.py --lint` still 0
- [x] 3.5 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
