## MODIFIED Requirements

### Requirement: Единый формат результата

Каждый прогон SHALL сохранять JSON с top-level `summary`: `passed`, `total`,
`pass_rate`, `total_seconds`, `total_steps`, `total_tokens`,
`total_input_tokens`, `total_output_tokens`, `total_reasoning_tokens`,
`total_cache_read_tokens`, `total_cache_write_tokens`, `estimated_cost_rub`.

#### Scenario: Отчёт подхватывается автосинком

- **WHEN** прогон сохранён в каталоге `results/`
- **THEN** `scripts/build_fork_results.py` SHALL включать его в авто-блок, если имя
  файла совпадает с разрешёнными паттернами и не входит в список исключений

#### Scenario: OpenClaw-раннер агрегирует шаги

- **WHEN** `run_openclaw_bench.py` записывает артефакт прогона в `_write_results(...)`
- **THEN** блок `summary` SHALL содержать `total_steps`, равный сумме per-task
  `agent_steps` (число вызовов инструментов), а SHALL NOT опускать это поле

#### Scenario: Явные cache-бакеты в summary

- **WHEN** `run_openclaw_bench.py` записывает артефакт прогона в `_write_results(...)`
- **THEN** блок `summary` SHALL содержать `total_cache_read_tokens` и
  `total_cache_write_tokens`, выведенные из per-task токенов (явные поля конверта,
  иначе `max(total_tokens - input - output, 0)`), а SHALL NOT опускать эти поля

#### Scenario: Reasoning-бакет в summary

- **WHEN** `run_openclaw_bench.py` записывает артефакт прогона
- **THEN** блок `summary` SHALL содержать `total_reasoning_tokens`, равный сумме
  per-task `agent_reasoning_tokens`

## ADDED Requirements

### Requirement: Pi-раннер записывает cache-бакеты

Раннер Pi SHALL читать `usage.cacheRead` и `usage.cacheWrite` каждой assistant-записи
Pi-потока и SHALL записывать их как per-task `agent_cache_read_tokens` /
`agent_cache_write_tokens` и как `summary.total_cache_read_tokens` /
`total_cache_write_tokens`, а SHALL NOT терять их.

#### Scenario: Cache-бакеты попадают в артефакт

- **WHEN** `run_pi_bench.py` записывает артефакт прогона
- **THEN** каждая задача SHALL содержать `agent_cache_read_tokens` и
  `agent_cache_write_tokens`, а `summary` — их суммы

#### Scenario: Cache-бакет учтён в ₽-стоимости

- **WHEN** `run_pi_bench._write_results` считает `estimated_cost_rub`
- **THEN** стоимость SHALL включать cache-бакет по политике резолвера
  (`harness_bench.cost_resolver`), а SHALL NOT считать cache как 0

### Requirement: Учёт токенов без задвоения

Оба раннера SHALL учитывать `usage` каждого ответа модели **ровно один раз**.
Pi-раннер SHALL считать `usage` только из события `message_end` (или одиночного
объекта, несущего `usage`), дедуплицируя по `responseId`, и SHALL NOT учитывать
повторы того же `usage` из `turn_end`, `agent_end.messages[]` и `message_update`.
OpenClaw-раннер SHALL считать `usage` один раз из конверта и SHALL NOT
пере-выводить cache-бакет, когда конверт содержит явные `cacheRead`/`cacheWrite`.

#### Scenario: Повторный usage не задваивает счёт

- **WHEN** один assistant-ответ присутствует в `message_end`, `turn_end` и
  `agent_end.messages[]`
- **THEN** его `input`/`output`/`reasoning`/`total` SHALL учитываться один раз,
  а SHALL NOT умножаться на число вхождений

#### Scenario: message_update не считается

- **WHEN** поток содержит множество `message_update`-дельт, несущих тот же `usage`
- **THEN** дельты SHALL NOT увеличивать счётчики токенов и число API-вызовов

#### Scenario: Инвариант бакетов артефакта

- **WHEN** артефакт прогона записан
- **THEN** `summary.total_tokens` SHALL равняться
  `total_input_tokens + total_output_tokens + total_cache_read_tokens +
  total_cache_write_tokens`

### Requirement: Провайдерская сверка ₽-стоимости gpt-5.5

Артефакты gpt-5.5 SHALL обеспечивать сходимость своей ₽-стоимости с провайдерской
выгрузкой Cloud.ru в пределах ±1% на сохранённом fixture-срезе
(`tests/fixtures/gpt55_provider_slice.csv`), где cached input тарифицируется по
входной ставке (`cost = input*854 + output*5124`).

#### Scenario: Pi-волна сходится с провайдером

- **WHEN** суммарная ₽-стоимость Pi-артефактов gpt-5.5 сравнивается со срезом
  провайдера для Pi-аккаунта (`oait`)
- **THEN** относительное расхождение SHALL быть в пределах ±1%

#### Scenario: Срез выгрузки в репозитории

- **WHEN** запускается регресс-тест сверки
- **THEN** он SHALL использовать обрезанный fixture-срез из `tests/fixtures/`,
  а SHALL NOT тянуть полную выгрузку
