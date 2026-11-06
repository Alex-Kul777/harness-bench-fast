# add-fork-profile-parity

## Why
Сверка с upstream-страницей (`ai-forever.github.io/harness-bench-fast`) показала два
расхождения в форматировании колонок:
1. **Model** — upstream пишет уровень ризонинга в самой модели (напр.
   `Claude Haiku 5.5 (OpenRouter) (default)`, `DeepSeek V4.1 Flash (OpenRouter) (high)`);
   у нас уровень лежал только в колонке Profile.
2. **Harness** — upstream пишет харнес **с версией** (напр. `pi-mono 0.73.1`,
   `OpenClaw 2026.9.6`, `Claude Code 2.1.300`, `Codex CLI 0.160.1`); у нас — только имя.

## What Changes
- `scripts/build_fork_home.py`: `Model` наших строк получает суффикс уровня ризонинга из
  профиля (`thinking: off` → `(thinking: off)`, `high` → `(high)`); не-ризонинговые
  профили (`MCP off`, `—`) — без суффикса (не выдумываем).
- `Harness`: суффикс версии добавляется **из артефакта прогона**
  (`harness_version`/`openclaw_version`/`cli_version`/`runner_version`), когда он записан.
- Наши артефакты версию харнеса **сейчас не пишут** → наши строки остаются без суффикса
  (фикс требует записи версии раннером — отдельная задача, см. design).

## Impact
- `scripts/build_fork_home.py`, `docs/fork.html`, `docs/fork-home-results.json`. Данные read-only.
- Upstream-строки не меняются (их модель уже содержит уровень).
