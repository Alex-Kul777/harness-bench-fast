# benchmark-runs

## MODIFIED Requirements

### Requirement: Раннеры живут в HBF

Бенчмарк-раннеры (`run_pi_bench.py`, `run_openclaw_bench.py`, `run_hermes_bench.py`)
SHALL быть доступны в корне репозитория HBF и SHALL запускаться из него без
необходимости в дополнительной директории `openclaw-workspace`.

#### Scenario: Запуск раннера из корня HBF

- **WHEN** пользователь клонирует HBF и выполняет `python3 run_pi_bench.py --help`
- **THEN** команда SHALL завершиться успешно и вывести help без ошибок импорта

#### Scenario: BENCH_DIR по умолчанию указывает на корень HBF

- **WHEN** `BENCH_DIR` не задан в окружении
- **THEN** раннер SHALL устанавливать `BENCH_DIR = Path(__file__).parent`,
  т.к. `harness_bench/` теперь co-located с раннерами в корне HBF

#### Scenario: Env override для совместимости

- **WHEN** задана переменная окружения `BENCH_DIR`
- **THEN** раннер SHALL использовать её значение как корень для `harness_bench`
  и `results/`, обеспечивая обратную совместимость с прежним расположением

#### Scenario: Расположение артефактов прогона

- **WHEN** раннер завершает прогон и сохраняет результат
- **THEN** файл SHALL быть записан в `results/` относительно корня HBF по умолчанию
