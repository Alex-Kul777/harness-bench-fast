# add-runner-suite-selector — proposal

## Why

Фаза 0 трека #428 показала: раннеры `run_pi_bench.py` и `run_openclaw_bench.py`
не умеют выбирать волну/суиту — только `--tasks`, `--pilot`, `--shot-list`
(у OpenClaw ещё `--all`, но это весь registry из 531 задачи). Чтобы прогнать
новую волну v0.21.3, приходится хардкодить десятки ID вручную. Нужен выбор
по имени волны.

## What Changes

- Новый флаг `--suite <name>` в обоих раннерах. Значения — ключи
  `harness_bench.tasks.SUITES` (`light`, `medium`, `medium-historical80`, `long`,
  `reflect`, `feasibility`, `general-hard`, `composite-hard`, `composite-hard-calibration`, `default`).
- Приоритет выбора: `--tasks` > `--suite` > `--pilot` > `--shot-list` / `--all`.
- Не **BREAKING**: прежние флаги работают как раньше.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `benchmark-runs` — добавляется требование о выборе
  волны по имени в раннерах.

## Out of scope

- Автоподбор `--timeout` по волне.
- Изменение scoring/верификаторов.
- Собственно прогоны моделей (платные) — это Фаза 2+ трека #428.

## Impact

- `benchmark-research/run_pi_bench.py`, `benchmark-research/run_openclaw_bench.py`
  (репозиторий `openclaw-workspace`). Задачи/registry не меняются.

## Tracking

- Workboard: `2d3c4426`; Epic: #428
