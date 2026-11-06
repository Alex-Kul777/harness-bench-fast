# add-fork-profile-date

## Why
Владелец заметил: в колонке `Profile` на `docs/fork.html` нет даты прогона, тогда как
в upstream/README она есть (`thinking: off (2026-11-04)`). Нужно проставлять дату
совершения бенчмарка.

## What Changes
- `scripts/build_fork_home.py`: дата прогона добавляется к `Profile` в формате
  `профиль (YYYY-MM-DD)`. Резолвер дат (по приоритету):
  1) `session_id` задач (напр. Hermes) → `YYYY-MM-DD`;
  2) имя файла `_YYYYMMDD`;
  3) курируемая README-таблица Shot List (наши строки);
  4) upstream — `measurement_date` из `leaderboard-results.json`.
- Если даты нет — Profile остаётся без суффикса (не выдумываем).
- Фикс: `*_thinking_off` файлы без модельного токена → модель `GLM-5.2`.

## Impact
- Только `scripts/build_fork_home.py` + `docs/*`. Данные read-only.
