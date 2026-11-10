## MODIFIED Requirements

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

## ADDED Requirements

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
