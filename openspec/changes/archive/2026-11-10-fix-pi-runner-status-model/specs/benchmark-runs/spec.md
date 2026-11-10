## ADDED Requirements

### Requirement: Статус-файл прогресса Pi-раннера

Pi-раннер SHALL писать статус-файл прогресса через `_write_status`, принимая модель
прогона явным параметром (`model`, по умолчанию `DEFAULT_MODEL`), и SHALL
использовать её для расчёта `estimated_cost_rub`. Запись статуса SHALL NOT
завершаться ошибкой `NameError` из-за отсутствующей привязки `model`.

#### Scenario: Статус для не-дефолтной модели

- **WHEN** прогон Pi выполняется с моделью, отличной от `DEFAULT_MODEL`, и включён статус-файл
- **THEN** `_write_status` SHALL записать JSON со `estimated_cost_rub`, рассчитанным по ставкам этой модели

#### Scenario: Прогон завершается без NameError

- **WHEN** все задачи прогона Pi обработаны и вызывается `_write_status(...)`
- **THEN** вызов SHALL завершиться успешно и SHALL NOT поднять `NameError`

#### Scenario: Вызовы из run_batch передают модель

- **WHEN** `run_batch` вызывает `_write_status` (в последовательной или в threaded ветке)
- **THEN** он SHALL передать активную модель прогона в параметр `model`
