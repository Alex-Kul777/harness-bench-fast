# Proposal: fix-pi-runner-status-model

## Why

`run_pi_bench.py` падает с `NameError: name 'model' is not defined` в
`_write_status(...)` (строка ~398) сразу после завершения прогона: функция
ссылается на `model`, но не получает его ни как параметр, ни из замыкания.
Оба вызова (~484 и ~507) передают только `path, completed, total_task_count,
results, started_at`. Любой прогон Pi с `--status-file` (long/reflect/feasibility
волны) аварийно завершается после последней задачи вместо записи статуса.

## What Changes

- `_write_status` получает новый параметр `model=DEFAULT_MODEL` и использует его
  при вызове `_get_model_rates(model or DEFAULT_MODEL)`.
- Оба call-site (`run_batch`, sequential и threaded ветки) передают
  `model=model`.
- Никакого иного изменения поведения: pass/fail, схема статуса и результаты не
  трогаются.
- Новый регрессионный тест `tests/test_runner_pi_status_model.py`: RED до фикса
  (`NameError`), GREEN после; проверяет, что статус пишется с корректной
  стоимостью для не-дефолтной модели.

## Capabilities

### New Capabilities
- (нет)

### Modified Capabilities
- `benchmark-runs`: добавляется требование, что Pi-раннер SHALL записывать
  статус-файл прогресса, принимая модель прогона, и SHALL NOT падать по
  `NameError` при записи статуса.

## Impact

- Код: `run_pi_bench.py` (`_write_status`, два call-site).
- Тесты: `tests/test_runner_pi_status_model.py` (новый);
  `tests/test_runner_pi_cleanup.py` остаётся green.
- Данные/схема артефактов не меняются; публикация не затрагивается.

## Out of scope

- Изменение методологии pass/fail, схемы артефактов или расчёта стоимости.
- Прочие раннеры (OpenClaw/Hermes) — их `_write_status` уже корректен.
