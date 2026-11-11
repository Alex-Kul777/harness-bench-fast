## ADDED Requirements

### Requirement: Override синтетической/неверной публичной cache-ставки

Когда публикуемая cache-ставка модели синтетическая или не соответствует фактическому
биллингу, система SHALL тарифицировать cache-read и cache-write токены по **входной**
ставке этой модели, а SHALL NOT использовать неверную публичную ставку. Override SHALL
задаваться явной таблицей «model id → `input` | ₽/1M» и SHALL NOT выводиться эвристикой.
Resolver SHALL вывести отличимый NOTE при override. Модели с корректной публичной
cache-ставкой SHALL оставаться незатронутыми.

#### Scenario: gpt-5.5 — синтетический cache-тариф → входная ставка

- **WHEN** каталог публикует `openai/gpt-5.5` `cache_read = 85.4` (= `input/10`), тогда как
  фактический биллинг — `input*854 + output*5124` с полным prompt по входной ставке
- **THEN** `resolve_model_rates("openai/gpt-5.5")` SHALL вернуть `cacheRead = 854.0`, а
  `compute_cost_rub` SHALL тарифицировать cache-бакет по 854 ₽/1M, а SHALL NOT по 85.4

#### Scenario: Составной id провайдера

- **WHEN** раннер передаёт `custom-foundation-models-api-cloud-ru/openai/gpt-5.5`
- **THEN** override SHALL применяться по совпадению суффикса `/openai/gpt-5.5`

#### Scenario: Отличимый NOTE при override

- **WHEN** `resolve_model_rates` применяет override синтетической/неверной cache-ставки
- **THEN** resolver SHALL вывести NOTE о том, что публичная cache-ставка синтетическая и
  cache тарифицируется по входной ставке, а SHALL NOT молчать

#### Scenario: Реальная cache-ставка не затрагивается

- **WHEN** модель публикует корректную cache-ставку (DeepSeek-V4.1-Flash `cache_read` = 6.5)
- **THEN** `resolve_model_rates` SHALL сохранить 6.5, SHALL NOT применять override и
  SHALL NOT выводить NOTE об override

#### Scenario: Бэкфилл не откатывает корректную стоимость

- **WHEN** `scripts/backfill_cost_rub.py` пересчитывает gpt-5.5-артефакт, чей
  `estimated_cost_rub` уже рассчитан с cache@input (сумма 61 966,63 ₽)
- **THEN** цена SHALL остаться неизменной, а артефакт SHALL NOT вернуться к cache@85.4
