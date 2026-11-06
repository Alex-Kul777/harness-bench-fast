# add-fork-upstream-rows

## Why
Единая форк-страница `docs/fork.html` показывала upstream-строки только для Light.
Владелец просит «правильно добавить результаты из основного» по всем наборам.

## What Changes
- `scripts/build_fork_home.py`: добавляет **upstream-строки** для
  **Shot List (52)** (из README «Shot List Leaderboard», наши харнессы исключены) и
  **Medium (80)** (из `docs/leaderboard-results.json`, поле `medium`). Light уже был.
- Групповые строки `Our runs` / `Upstream comparison` — уже в шаблоне, работают для всех табов.
- Docs: `FORK.md` ссылается на `fork.html`; `docs/fork-results.md` пересобран.

## Impact
- Только `scripts/build_fork_home.py` + `docs/*`. Upstream-данные read-only.
