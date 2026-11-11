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
  `total_cache_write_tokens`, выведенные один раз из per-task токенов (или
  `max(total_tokens - input - output, 0)` при отсутствии явных cache-полей), а
  SHALL NOT опускать эти поля

#### Scenario: Hermes-раннер записывает cache и reasoning бакеты

- **WHEN** `run_hermes_bench.py` записывает артефакт прогона в `_write_results(...)`
- **THEN** блок `summary` SHALL содержать `total_cache_read_tokens`,
  `total_cache_write_tokens` и `total_reasoning_tokens`, выведенные один раз из
  per-task токенов (явные cache-поля, иначе `max(total_tokens - input - output, 0)`),
  а SHALL NOT опускать эти поля

#### Scenario: Hermes-раннер агрегирует шаги

- **WHEN** `run_hermes_bench.py` записывает артефакт прогона в `_write_results(...)`
- **THEN** блок `summary` SHALL содержать `total_steps`, равный сумме per-task
  `agent_steps`, а SHALL NOT опускать это поле

## ADDED Requirements

### Requirement: Hermes-раннер: шапка метаданных артефакта

Артефакт прогона Hermes SHALL содержать top-level поля `harness` (= `"hermes"`),
`thinking`, `task_set_version`, `model` и — когда версия известна — `harness_version`,
записанные через общий helper `harness_bench.artifact_metadata`.

#### Scenario: Все поля шапки записаны

- **WHEN** `run_hermes_bench._write_results` записывает артефакт
- **THEN** артефакт SHALL содержать строковые `harness="hermes"`, `thinking`,
  `task_set_version` и `model`, а `task_set_version` SHALL выводиться из задач прогона
  через `task_set_version_for_tasks`

#### Scenario: Версия харнеса записана при известности

- **WHEN** `run_hermes_bench` определяет версию через `--harness-version`, env
  `HARNESS_BENCH_HARNESS_VERSION` или autodetect (`hermes --version`)
- **THEN** поле `harness_version` SHALL присутствовать и равняться этой версии

#### Scenario: Версия харнеса неизвестна

- **WHEN** ни флаг, ни env, ни autodetect не дали версию
- **THEN** поле `harness_version` SHALL отсутствовать в артефакте (SHALL NOT выдумываться)

#### Scenario: Версия набора задач волны

- **WHEN** прогон Hermes содержит задачи waves 17–19 (диапазон 392–471)
- **THEN** записанная `task_set_version` SHALL NOT быть `"0.16.0"` и SHALL равняться
  версии соответствующей волны

### Requirement: Hermes-раннер: ставки модели и cache-бакет в ₽-стоимости

`run_hermes_bench` SHALL вычислять `estimated_cost_rub` через
`harness_bench.cost_resolver.resolve_model_rates(model)` и `compute_cost_rub`,
а SHALL NOT применять хардкод-константы GLM-5.2 (239.12/751.52). Cache-бакет SHALL
включаться в стоимость по политике резолвера.

#### Scenario: DeepSeek-V4.1-Flash считается по своим ставкам

- **WHEN** `run_hermes_bench` считает стоимость для модели DeepSeek-V4.1-Flash
- **THEN** `estimated_cost_rub` SHALL рассчитываться по ставкам 64.94/194.81/6.5/0 ₽/1M,
  а SHALL NOT по fallback GLM-5.2

#### Scenario: Cache-бакет учтён в стоимости

- **WHEN** `run_hermes_bench._write_results` считает `estimated_cost_rub`
- **THEN** стоимость SHALL включать cache-read/cache-write бакет, а SHALL NOT считать
  cache как 0

#### Scenario: Статус-файл использует модель прогона

- **WHEN** `run_batch` вызывает `_write_status` для модели, отличной от `DEFAULT_MODEL`
- **THEN** `estimated_cost_rub` статуса SHALL считаться по ставкам активной модели

### Requirement: Hermes-раннер: уровень thinking

`run_hermes_bench` SHALL принимать флаг `--thinking <level>`
(none|minimal|low|medium|high|xhigh|max|ultra) и SHALL прокидывать его в
`hermes chat --reasoning <level>`; `--thinking-off` SHALL оставаться алиасом
`--thinking none`. Уровень SHALL записываться в top-level `thinking`, а при
отсутствии — `"default"`.

#### Scenario: Уровень прокинут в CLI и записан

- **WHEN** раннер запущен с `--thinking high`
- **THEN** вызов `hermes chat` SHALL содержать `--reasoning high`, а поле `thinking`
  артефакта SHALL равняться `"high"`

#### Scenario: thinking-off как алиас none

- **WHEN** раннер запущен с `--thinking-off`
- **THEN** это SHALL эквивалентно `--thinking none`, и поле `thinking` SHALL равняться `"none"`

#### Scenario: Уровень не задан

- **WHEN** ни `--thinking`, ни `--thinking-off` не заданы
- **THEN** поле `thinking` SHALL равняться `"default"`

### Requirement: Hermes-раннер: совместимость прогона

`run_hermes_bench` SHALL сохранять поведение memory-задач (222–253) — они SHALL
запускаться без `--ignore-rules`, чтобы AGENTS.md инжектился — и SHALL использовать
провайдер `custom` с `OPENAI_BASE_URL`/`OPENAI_API_KEY`.

#### Scenario: Memory-задачи получают AGENTS.md

- **WHEN** раннер запускает memory-задачу (222–253)
- **THEN** команда `hermes chat` SHALL NOT содержать `--ignore-rules`

#### Scenario: Провайдер custom

- **WHEN** раннер запускает любую задачу
- **THEN** окружение вызова SHALL содержать `OPENAI_BASE_URL` и `OPENAI_API_KEY`
  для `--provider custom`
