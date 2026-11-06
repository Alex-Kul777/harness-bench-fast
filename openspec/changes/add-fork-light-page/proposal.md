# add-fork-light-page

## Why
Форк публикует Medium 80 (`docs/fork-medium90.html`) и capability-сэмпл
(`docs/fork-sample.html`), но **Light (391)** — самый крупный набор наших прогонов
(Hermes / Pi / OpenClaw + GLM-5.2) — живёт только в markdown `docs/fork-results.md`.
Владелец не нашёл Light-таблицу с нашими результатами на сайте.

## What Changes
- Новый генератор `scripts/build_fork_light.py`: собирает **наши** полные Light-прогоны
  (явный allow-list источников) и **upstream**-строки Light (из `docs/leaderboard-results.json`),
  пишет `docs/fork-light-results.json` + `docs/fork-light.html`.
- Страница `docs/fork-light.html`: канонические колонки (Profile / Time / Steps /
  Tokens (cost)), ссылки на исходные JSON, отдельная upstream-таблица для сравнения.
- Nav-ссылка `Light (391)` на страницах `docs/fork-medium90.html` и `docs/fork-sample.html`.

## Impact
- Только `docs/` и `scripts/`. Прогоны/задачи не меняются; upstream-данные читаются read-only.
