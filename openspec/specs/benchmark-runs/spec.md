# benchmark-runs

## Purpose

Определяет, как форк запускает бенчмарк-прогоны (Light 391, Medium 90, wave 19 —
задачи 432–471) на харнессах Pi / OpenClaw / Hermes / opencode и как результаты
сохраняются для последующей публикации.

## Requirements

### Requirement: Выбор suite

Система SHALL поддерживать выбор suite: `light` (задачи 1–391), `medium` (90 задач)
и явный диапазон задач для wave 19 (`432–471`).

#### Scenario: Запуск Light

- **WHEN** пользователь запускает раннер с `--suite light`
- **THEN** прогоняются задачи 1–391, и результат сохраняется как JSON с блоком `summary`

#### Scenario: Wave 19 требует изоляции

- **WHEN** выборка содержит задачи 432–471
- **THEN** запуск SHALL требовать Linux/bwrap-изоляцию (`--isolation bwrap`) и SHALL
  отклоняться до вызова модели при её отсутствии

### Requirement: Единый формат результата

Каждый прогон SHALL сохранять JSON с top-level `summary`: `passed`, `total`,
`pass_rate`, `total_seconds`, `total_steps`, `total_tokens`,
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

### Requirement: Выбор волны в раннерах

Раннеры Pi и OpenClaw SHALL поддерживать выбор волны по имени через флаг
`--suite`, где имена совпадают с ключами `harness_bench.tasks.SUITES`.

#### Scenario: Прогон новой волны по имени

- **WHEN** раннер запускается с `--suite reflect`
- **THEN** выбираются задачи волны tool-reflection (412–431) из registry v0.21.3,
  и запуск идёт без явного перечисления ID

#### Scenario: Приоритет явного списка

- **WHEN** заданы одновременно `--tasks` и `--suite`
- **THEN** SHALL использоваться явный список `--tasks`

#### Scenario: Неизвестное имя волны

- **WHEN** передан `--suite` со значением, которого нет в `SUITES`
- **THEN** раннер SHALL завершиться с ошибкой до запуска задач, перечислив допустимые имена

### Requirement: Pi-раннер опирается на санитарный timeout

Поскольку базовый `pi-agent` не предоставляет управление лимитом шагов, Pi-раннер
SHALL использовать санитарный `--timeout` как единственный ограничитель времени
прогона и SHALL NOT эмулировать лимит шагов (синтетический счётчик или подмену на
иной механизм).

#### Scenario: Ограничение прогона

- **WHEN** `run_pi_bench.py` запускает задачу
- **THEN** ограничение SHALL задаваться только через `--timeout` (плюс
  `--concurrency`), без какого-либо шаг-капа

#### Scenario: Запрос шаг-капа

- **WHEN** запрошен лимит шагов, не поддерживаемый базовым агентом
- **THEN** раннер SHALL NOT подменять его скрытой эмуляцией; ограничение
  документируется, а не имитируется

### Requirement: Эффективный таймаут с учётом floors задач

Pi-раннер SHALL вычислять эффективный таймаут задачи как
`max(--timeout, task.min_timeout_seconds)`, обрезая `task.max_timeout_seconds`
(семантика `effective_task_timeout`), и SHALL записывать эффективный таймаут в
JSON-результат прогона.

#### Scenario: Floor поднимает таймаут

- **WHEN** задача long с `min_timeout_seconds = 7200` запускается с `--timeout 2400`
- **THEN** эффективный таймаут SHALL быть `7200`, а не `2400`

#### Scenario: Max обрезает таймаут

- **WHEN** у задачи `min_timeout_seconds = max_timeout_seconds = 3600`, а передан `--timeout 7200`
- **THEN** эффективный таймаут SHALL быть `3600`

### Requirement: Таймаут ниже флора не применяется молча

Конечный `--timeout` ниже `task.min_timeout_seconds` SHALL отклоняться (задача
пропускается/поднимается до флора), если не задан явный opt-in; при opt-in прогон
SHALL помечаться как несопоставимый (`comparable: false`).

#### Scenario: Осознанный cost-cap

- **WHEN** задан `--allow-below-floor` с таймаутом ниже флора
- **THEN** задача выполняется, но результат SHALL быть помечен несопоставимым

### Requirement: Версия харнеса в артефакте

Артефакт прогона SHALL содержать поле верхнего уровня `harness_version` (строка), когда
версия харнеса задана. Раннер `run-cli` SHALL принимать версию через флаг
`--harness-version` и через переменную окружения `HARNESS_BENCH_HARNESS_VERSION`
(флаг приоритетнее). При отсутствии значения поле SHALL отсутствовать в артефакте (версия
SHALL NOT выдумываться).

#### Scenario: Версия задана флагом

- **WHEN** `run-cli` запущен с `--harness-version "pi-mono 0.73.1"`
- **THEN** записанный артефакт SHALL содержать `harness_version = "pi-mono 0.73.1"`

#### Scenario: Версия задана через окружение

- **WHEN** задан `HARNESS_BENCH_HARNESS_VERSION` и флаг не передан
- **THEN** значение SHALL попасть в `harness_version` артефакта

#### Scenario: Версия не задана

- **WHEN** ни флаг, ни env не заданы
- **THEN** поле `harness_version` SHALL отсутствовать в артефакте

#### Scenario: Изоляция между прогонами

- **WHEN** прогон завершился (успешно или с прерыванием)
- **THEN** установленное значение версии SHALL сбрасываться (не утекает в следующий прогон
  в том же процессе)

### Requirement: Полная метаданных-шапка артефакта прогона

Артефакт прогона SHALL содержать top-level поля с точными именами: `harness`
(строка), `harness_version` (строка), `thinking` (строка — уровень reasoning),
`task_set_version` (строка) и `model` (строка). Раннеры Pi, OpenClaw и Hermes
SHALL записывать этот набор через общий helper `harness_bench.artifact_metadata`.

#### Scenario: Все поля записаны

- **WHEN** любой из трёх раннеров записывает артефакт прогона через `_write_results`
- **THEN** артефакт SHALL содержать top-level `harness`, `thinking`, `task_set_version` и `model` как строки

#### Scenario: Уровень reasoning задан

- **WHEN** прогон запущен с явным уровнем reasoning (например `--thinking high`)
- **THEN** поле `thinking` SHALL равняться этому уровню

#### Scenario: Уровень reasoning не задан

- **WHEN** уровень reasoning не задан явно
- **THEN** поле `thinking` SHALL равняться строке `"default"`

#### Scenario: Версия харнесса известна

- **WHEN** версия харнесса задана флагом, env или autodetect
- **THEN** поле `harness_version` SHALL присутствовать и равняться этой версии

#### Scenario: Версия харнесса неизвестна

- **WHEN** ни флаг, ни env, ни autodetect не дали версию харнесса
- **THEN** поле `harness_version` SHALL отсутствовать в артефакте (SHALL NOT выдумываться)

### Requirement: Корректная версия набора задач для волны

Раннеры SHALL выводить `task_set_version` из задач прогона через ревизии
`harness_bench.versioning.TASK_SET_REVISIONS`, а не из хардкод-константы. Для
прогонов waves 17–19 (задачи 392–471) записанная `task_set_version` SHALL NOT
равняться `"0.16.0"` и SHALL соответствовать версии этой волны.

#### Scenario: Wave 17–19 не записывается как 0.16.0

- **WHEN** конфиг прогона содержит задачи из waves 17–19 (диапазон 392–471)
- **THEN** записанная `task_set_version` SHALL NOT быть `"0.16.0"` и SHALL равняться версии соответствующей волны

#### Scenario: Light остаётся 0.16.0

- **WHEN** прогон содержит только задачи Light (1–391)
- **THEN** записанная `task_set_version` SHALL равняться `"0.16.0"`

#### Scenario: Пустой набор задач

- **WHEN** список задач пуст или номера задач не распознаны
- **THEN** раннер SHALL записать текущую `TASK_SET_VERSION` реестра

### Requirement: Детекция модели артефакта для ₽-учёта

Бэкфилл (`scripts/backfill_cost_rub.py`) SHALL определять модель артефакта: по полям
(`model`, `summary.model`, `model` задачи, `command`), а если все поля пусты — по имени
файла из явной карты. Явные поля SHALL иметь приоритет над именем файла.

`resolve_model_rates(model_id, filename=None)` SHALL применять карту подсказок «имя файла
→ канонический id» последним средством перед fallback; бэкфилл SHALL передавать `filename`.

#### Scenario: Карта подсказок «имя файла → id»

- **WHEN** `model_id` не даёт ставок, а имя файла содержит один из токенов карты
- **THEN** подсказка SHALL разрешаться так: `gigachat3pro` → `GigaChat/GigaChat-3-Pro`,
  `giga35` → `ai-sage/GigaChat3.5-432B-A28B-Reasoning`, `glm52` → `zai-org/GLM-5.2`,
  `glm53` → `zai-org/GLM-5.3`, `qwen36` → `Qwen/Qwen3.6-35B-A3B`, `oss120b` →
  `openai/gpt-oss-120b`, `minimaxm3` → `MiniMaxAI/MiniMax-M3`, `ds41flash` →
  `deepseek-ai/DeepSeek-V4.1-Flash`

#### Scenario: Pi-артефакт без поля model

- **WHEN** артефакт содержит только `results` и `summary` (без `model` и `command`), а имя
  файла содержит `ds41flash`
- **THEN** модель SHALL определиться как
  `custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash`

#### Scenario: Семейство GigaChat 3.5 по имени файла

- **WHEN** имя артефакта содержит `giga35` или `gigachat35`
- **THEN** модель SHALL определиться как `ai-sage/GigaChat3.5-432B-A28B-Reasoning`

#### Scenario: Семейство GigaChat 3 Pro по имени файла

- **WHEN** имя артефакта содержит `gigachat3pro`, а поля модели отсутствуют
- **THEN** модель SHALL определиться как `GigaChat/GigaChat-3-Pro`, `estimated_cost_rub`
  SHALL считаться по её входной/выходной ставке (73.03/176.39 ₽/1M), а cache-бакет —
  по входной ставке (нет публичного cache-тарифа), а SHALL NOT использовать fallback GLM-5.2

#### Scenario: Явное поле модели имеет приоритет

- **WHEN** артефакт содержит поле `model`, отличное от семейства в имени файла
- **THEN** бэкфилл SHALL использовать значение поля, а SHALL NOT переопределять его именем файла

### Requirement: Ставки определённой модели и fallback только для неопределимых

Расчёт `estimated_cost_rub` SHALL использовать ставки именно определённой модели. Когда
модель определима, бэкфилл SHALL NOT применять fallback GLM-5.2. При действительно
неопределимой модели бэкфилл SHALL использовать задокументированный fallback
(GLM-5.2), а resolver SHALL вывести предупреждение в stderr.

#### Scenario: Pi-артефакт считается по ставкам модели

- **WHEN** модель артефакта определена как DeepSeek-V4.1-Flash
- **THEN** `estimated_cost_rub` SHALL вычисляться по ставкам 64.94/194.81/6.5/0 ₽/1M,
  а SHALL NOT использовать fallback GLM-5.2

#### Scenario: Неизвестная модель — fallback с предупреждением

- **WHEN** ни поля, ни имя файла не позволяют определить модель
- **THEN** бэкфилл SHALL использовать задокументированный fallback GLM-5.2
  (239.12/751.52/0/0), а resolver SHALL вывести предупреждение в stderr

### Requirement: Учёт cache-read бакета в ₽-стоимости

Раннер и бэкфилл SHALL хранить cache-бакет явно в
`summary.total_cache_read_tokens` и `summary.total_cache_write_tokens`. Когда артефакт
их не хранит, система SHALL вывести `cache_read = max(total_tokens - input - output, 0)`
один раз и SHALL записать результат обратно. Бэкфилл SHALL предпочитать явные бакеты и
SHALL NOT выводить их заново, когда они есть.

#### Scenario: Cache-read восстановлен из total_tokens

- **WHEN** артефакт хранит `total_input_tokens`, `total_output_tokens` и `total_tokens`,
  но не хранит `total_cache_read_tokens`
- **THEN** `estimated_cost_rub` SHALL рассчитываться с cache-read =
  `total_tokens - input - output` по ставке модели и SHALL NOT занижать стоимость

#### Scenario: Явный cache-read не перезаписывается

- **WHEN** артефакт хранит явное поле `total_cache_read_tokens`
- **THEN** система SHALL использовать его как есть и SHALL NOT переопределять его из `total_tokens`

#### Scenario: Явные бакеты записаны раннером

- **WHEN** `run_openclaw_bench._write_results` получает per-task записи с
  `agent_total_tokens`, но без явных cache-полей
- **THEN** `summary.total_cache_read_tokens` SHALL равняться
  `max(total_tokens - input - output, 0)`, а выведенное значение SHALL быть записано и
  в per-task запись явно

#### Scenario: Бэкфилл предпочитает явный бакет

- **WHEN** артефакт хранит `summary.total_cache_read_tokens`
- **THEN** бэкфилл SHALL использовать его как есть и SHALL NOT переопределять его из `total_tokens`

#### Scenario: Старый артефакт без явного бакета

- **WHEN** артефакт не хранит `total_cache_read_tokens`, но хранит `total_tokens`
- **THEN** бэкфилл SHALL вывести `cache_read = total_tokens - input - output` и записать
  его в артефакт как явный бакет

### Requirement: Тариф cache-бакета при отсутствии публичного cache-тарифа

Когда у определённой модели нет публичного cache-тарифа (`cacheRead`/`cacheWrite`
отсутствует, `None` или `0`), система SHALL тарифицировать cache-read и cache-write
токены по **входной** ставке той же модели. Публичная cache-ставка SHALL сохраняться как
есть (например DeepSeek-V4.1-Flash `cacheRead` = 6.5 ₽/1M). Resolver SHALL вывести
отличимый NOTE для модели без публичного cache-тарифа и SHALL NOT применять эту политику,
когда cache-ставка публичная.

#### Scenario: Нет cache-тарифа → входная ставка

- **WHEN** модель публикует `cache_read = 0.0` (напр. MiniMax-M3 или GigaChat-3-Pro)
- **THEN** cache-read бакет SHALL тарифицироваться по входной ставке модели, а SHALL NOT как 0
  (для MiniMax-M3 это даёт 8635.58 ₽ вместо 1234.93 ₽; для GigaChat-3-Pro — 956.96 ₽ вместо 62.12 ₽)

#### Scenario: Публичная cache-ставка сохраняется

- **WHEN** модель публикует `cache_read > 0` (напр. DeepSeek-V4.1-Flash = 6.5)
- **THEN** cache-read бакет SHALL тарифицироваться по публичной ставке 6.5 ₽/1M, а
  SHALL NOT по входной ставке (стоимость артефакта остаётся 572.89 ₽)

#### Scenario: Отличимый NOTE об отсутствии cache-тарифа

- **WHEN** `resolve_model_rates` разрешает модель без публичного cache-тарифа
- **THEN** resolver SHALL вывести NOTE, различающий «публичная cache-ставка» и «нет
  cache-тарифа → входная ставка», а SHALL NOT делать это молча

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
