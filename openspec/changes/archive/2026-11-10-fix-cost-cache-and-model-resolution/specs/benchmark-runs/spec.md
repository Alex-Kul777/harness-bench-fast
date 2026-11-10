## ADDED Requirements

### Requirement: Учёт cache-read бакета в ₽-стоимости

Система SHALL тарифицировать cache-read бакет, даже когда артефакт не хранит явного
cache-поля. Если `total_cache_read_tokens` и `total_cache_write_tokens` отсутствуют или
равны нулю, но известен `total_tokens`, раннер и бэкфилл SHALL восстанавливать
`cache_read = max(total_tokens - input - output, 0)` и SHALL включать его в
`estimated_cost_rub` по ставке `cacheRead` определённой модели.

#### Scenario: Cache-read восстановлен из total_tokens

- **WHEN** артефакт хранит `total_input_tokens`, `total_output_tokens` и `total_tokens`,
  но не хранит `total_cache_read_tokens`
- **THEN** `estimated_cost_rub` SHALL рассчитываться с cache-read =
  `total_tokens - input - output` по ставке модели и SHALL NOT занижать стоимость

#### Scenario: Явный cache-read не перезаписывается

- **WHEN** артефакт хранит явное поле `total_cache_read_tokens`
- **THEN** система SHALL использовать его как есть и SHALL NOT переопределять его из `total_tokens`

## MODIFIED Requirements

### Requirement: Детекция модели артефакта для ₽-учёта

Бэкфилл ₽-стоимости (`scripts/backfill_cost_rub.py`) SHALL определять модель артефакта:
сначала по полям (`model`, `summary.model`, `model` первой задачи, `command`), затем —
только если все поля пусты — по имени файла/семейства из явной небольшой карты. Явные
поля SHALL иметь приоритет над именем файла.

Resolver стоимости `harness_bench.cost_resolver.resolve_model_rates` SHALL принимать
опциональный аргумент `filename` и, если переданный `model_id` не даёт ставок, SHALL
применять последним средством перед fallback карту подсказок «имя файла → канонический
id»: `gigachat3pro` → `GigaChat/GigaChat-3-Pro`, `giga35` →
`ai-sage/GigaChat3.5-432B-A28B-Reasoning`, `glm52` → `zai-org/GLM-5.2`, `glm53` →
`zai-org/GLM-5.3`, `qwen36` → `Qwen/Qwen3.6-35B-A3B`, `oss120b` →
`openai/gpt-oss-120b`, `minimaxm3` → `MiniMaxAI/MiniMax-M3`, `ds41flash` →
`deepseek-ai/DeepSeek-V4.1-Flash`. Бэкфилл SHALL передавать имя артефакта в resolver.

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
- **THEN** модель SHALL определиться как `GigaChat/GigaChat-3-Pro` и `estimated_cost_rub`
  SHALL считаться по ставкам 73.03/176.39/0/0 ₽/1M, а SHALL NOT использовать fallback GLM-5.2

#### Scenario: Явное поле модели имеет приоритет

- **WHEN** артефакт содержит поле `model`, отличное от семейства в имени файла
- **THEN** бэкфилл SHALL использовать значение поля, а SHALL NOT переопределять его именем файла
