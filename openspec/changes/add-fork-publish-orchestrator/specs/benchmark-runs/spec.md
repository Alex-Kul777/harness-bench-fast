# benchmark-runs (delta)

## ADDED Requirements

### Requirement: Автозапуск публикации после прогона

Раннеры `run_pi_bench.py` и `run_openclaw_bench.py` SHALL поддерживать флаг `--publish`
(по умолчанию включён) и парный `--no-publish`, и по завершении прогона SHALL вызывать
оркестратор `scripts/publish_fork.py` для созданного артефакта.

#### Scenario: Прогон завершён

- **WHEN** прогон завершается и `--publish` активен
- **THEN** SHALL быть вызван `scripts/publish_fork.py` для артефакта прогона

#### Scenario: Опт-аут

- **WHEN** передан `--no-publish`
- **THEN** публикация SHALL NOT запускаться
