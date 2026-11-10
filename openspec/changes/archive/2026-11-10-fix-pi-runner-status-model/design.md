# Design: fix-pi-runner-status-model

## Context

`_write_status(path, completed, total_task_count, results, started_at)` вызывает
`_get_model_rates(model or DEFAULT_MODEL)`, но `model` не является её параметром и
не виден из области видимости — получается `NameError` после завершения прогона.
Оба вызывающих места (~484 и ~507 в `run_pi_bench.py`) уже имеют `model` в
области видимости (параметр `run_batch`).

## Decision

Добавить `model=DEFAULT_MODEL` в сигнатуру `_write_status` и передавать
`model=model` в обоих call-site. Это минимальное изменение, не затрагивающее
схему статуса и не меняющее поведение ни при каких входных данных, кроме
устранения `NameError`.

Альтернатива — читать модель из глобального состояния: отклонено, потому что
раннер потокобезопасно параметризован моделью и глобал скрыл бы ошибку.

## Risks

- Низкий: изменение только добавляет параметр с дефолтом; вызовы без модели
  сохраняют прежний (дефолтный) расчёт ставок.
- Тест `tests/test_runner_pi_cleanup.py` не трогает `_write_status`, поэтому
  остаётся green.

## Verification

- `tests/test_runner_pi_status_model.py` RED до фикса, GREEN после.
- `tests/test_runner_pi_cleanup.py` green.
- `openspec validate --all --strict` == 0.
