# add-runner-suite-selector — tasks

## 1. Раннеры

- [x] 1.1 `run_pi_bench.py`: добавить `--suite` (choices из `harness_bench.tasks.SUITES`) + приоритет выбора (`--tasks` > `--suite` > `--pilot` > `--shot-list`)
- [x] 1.2 `run_openclaw_bench.py`: то же, сохранив `--all` как есть

## 2. Тесты

- [x] 2.1 Добавить `tests/test_runner_suite_selector.py`: `--suite reflect` даёт те же ID, что `SUITES['reflect']`; `--tasks` перебивает `--suite`

## 3. QA / верификация

- [x] 3.1 `--help` обоих раннеров показывает `--suite`; `python3 -m pytest tests/test_runner_suite_selector.py -q` зелёный
- [x] 3.2 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` = exit 0
