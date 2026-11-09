# benchmark-runs (delta)

## ADDED Requirements

### Requirement: Детекция модели артефакта для ₽-учёта

Бэкфилл ₽-стоимости (`scripts/backfill_cost_rub.py`) SHALL определять модель артефакта:
сначала по полям (`model`, `summary.model`, `model` первой задачи, `command`), затем —
только если все поля пусты — по имени файла/семейства из явной небольшой карты. Явные
поля SHALL иметь приоритет над именем файла.

#### Scenario: Pi-артефакт без поля model

- **WHEN** артефакт содержит только `results` и `summary` (без `model` и `command`), а имя
  файла содержит `ds41flash`
- **THEN** модель SHALL определиться как
  `custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash`

#### Scenario: Семейство GigaChat 3.5 по имени файла

- **WHEN** имя артефакта содержит `giga35` или `gigachat35`
- **THEN** модель SHALL определиться как `ai-sage/GigaChat3.5-432B-A28B-Reasoning`

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
