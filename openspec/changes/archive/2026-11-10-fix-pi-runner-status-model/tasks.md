# Tasks: fix-pi-runner-status-model

- [x] Добавить параметр `model=DEFAULT_MODEL` в `_write_status` (`run_pi_bench.py`)
- [x] Передать `model=model` в обоих call-site `_write_status` (~484 и ~507)
- [x] Добавить регрессионный тест `tests/test_runner_pi_status_model.py`
- [x] QA: новый тест RED до фикса, GREEN после
- [x] QA: `pytest tests/test_runner_pi_cleanup.py -q` green
- [x] QA: `openspec validate --all --strict` == 0
