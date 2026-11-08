# fix-fork-steps-column

## Why

Столбец **Steps** в таблицах форка пуст (`—`) у всех строк OpenClaw, хотя данные о шагах
есть: per-task `agent_steps` присутствуют, и их сумма (напр. 244/224/244 для прогонов
DeepSeek-V4.1-Flash 2026-11-07) в точности равна искомому значению. Причина —
раннер `run_openclaw_bench.py` не кладёт агрегат `total_steps` в блок `summary`, тогда как
спека `benchmark-runs` («Единый формат результата») его **требует**, а читающие генераторы
(`build_fork_home.py`, `build_fork_results.py`) берут только агрегат. Нужно восстановить
соответствие спеке и заполнить колонку, не искажая метрику.

## What Changes

- **Раннер OpenClaw** (`run_openclaw_bench.py`, репозиторий `openclaw-workspace`): в
  `_write_results(...)` в блок `summary` добавляется агрегат `total_steps` = Σ per-task
  `agent_steps` (приводит артефакт в соответствие с `benchmark-runs`).
- **Генераторы форка** (`scripts/build_fork_home.py`, `scripts/build_fork_results.py`):
  столбец `Steps` заполняется по приоритету — агрегат `summary.total_steps`, затем
  top-level `steps`, затем **fallback** Σ `tasks[].agent_steps`. `—` показывается **только**
  если шагов нет ни в одном источнике.
- **Бэкфилл исторических артефактов**: в уже закоммиченные `results/oc_shotlist_*.json`
  добавляется `summary.total_steps`, вычисленный из их же per-task данных (без пере-прогонов).
- **Тесты**: юнит-тест на fallback-агрегацию (generator) и на наличие `total_steps` в
  артефакте раннера; паритет RU/EN сохраняется (не ломается).
- **Метрика не меняется**: `Steps` = сумма шагов агента (`agent_steps` = `toolSummary.calls`);
  апстрим-строки и прогоны Pi/Hermes не затрагиваются.

## Capabilities

### New Capabilities

_(нет)_

### Modified Capabilities

- `result-reporting`: рендер колонки `Steps` SHALL заполняться из агрегата с fallback на
  сумму per-task `agent_steps` (никакого `—`, если per-task шаги есть).
- `benchmark-runs`: требование «Единый формат результата» уточняется явным сценарием, что
  OpenClaw-раннер SHALL писать `summary.total_steps` (агрегат per-task `agent_steps`).

## Impact

- `scripts/build_fork_home.py`, `scripts/build_fork_results.py`, `tests/` (harness-bench-fast).
- `run_openclaw_bench.py` (репозиторий `openclaw-workspace`, отдельная ветка).
- Регенерируемые `docs/fork.html`(+`.en`), `docs/fork-results.md`(+`.en`); закоммиченные
  `results/oc_shotlist_*.json`.
- **Out of scope:** изменение смысла метрики Steps; строки upstream; прогоны Pi/Hermes;
  cost-колонка (отдельный нюанс, не входит); backfill незакоммиченных копий в shared store.

## Workboard

- Card: `3f4b26cf` (board `project-a`).
