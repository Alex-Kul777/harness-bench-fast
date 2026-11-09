# Design: fix-cost-model-detection

## Контекст

Детекция модели нужна бэкфиллу, чтобы выбрать ставки для `estimated_cost_rub`.
Существующие артефакты делятся на два вида:

- **OpenClaw / Hermes**: несут поле `model` (или per-task `model`) → детекция по полям
  работает (`oc_medium_*_ds41flash_*` → DeepSeek).
- **Pi**: несут только `results` + `summary` (нет `model`, нет `command`) → детекция
  по полям даёт `None` → fallback GLM-5.2 (неверно).

## Решение (ADR-inline)

**Решение:** добавить в `scripts/backfill_cost_rub.py` последний, явный и узкий
источник модели — имя файла/семейство (`_FILENAME_MODEL_TOKENS`), применяемый
**только** когда ни одно поле не дало модели.

Почему имя файла:

1. Соглашение об именовании артефактов уже кодирует модель: `scripts/fork_metadata.py`
   (`MODEL_TOKENS`) тем же приёмом классифицирует `ds41flash`→DeepSeek-V4.1-Flash,
   `giga35`→GigaChat 3.5 Reasoning. Мы переиспользуем это соглашение, не меняя
   `fork_metadata`.
2. Альтернатива «писать модель в артефакты Pi» требует правки раннеров (вне scope) и
   не лечит уже закоммиченные артефакты.
3. Альтернатива «читать `harness_version`/`session_id`» — хрупко и неоднозначно.

Почему карта живёт в `backfill_cost_rub.py`, а не в `cost_resolver.py`: resolver
резолвит ставки для *уже известного* id и не знает про имена файлов; инференс из имени —
обязанность конкретного потребителя (бэкфилла). Публичный API resolver остаётся
нетронутым.

## Карта (явная, минимальная)

| Токен в имени файла | Канонический model id | Ставки ₽/1M (input/output/cacheRead/cacheWrite) |
|---|---|---|
| `ds41flash`  | `custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash` | 64.94 / 194.81 / 6.5 / 0 |
| `gigachat35` | `ai-sage/GigaChat3.5-432B-A28B-Reasoning` | 96.22 / 288.6 / 0 / 0 |
| `giga35`     | `ai-sage/GigaChat3.5-432B-A28B-Reasoning` | 96.22 / 288.6 / 0 / 0 |

Длинные/специфичные токены проверяются первыми. `giga35` — подстрока, которая НЕ
содержится в `gigachat35`, поэтому порядок между ними не критичен, но задан явно.

Ставки берёт существующий resolver (каталог-кэш Cloud.ru `> ~/.openclaw/openclaw.json
> fallback`); карта задаёт только *id*, а не ставки — единственный источник истины по
числам остаётся у resolver/каталога.

## Порядок детекции (после изменения)

1. `data["model"]`
2. `data["summary"]["model"]`
3. `model` первой задачи из `tasks`/`results`
4. первый «/»-токен из `command`
5. **имя файла** (`_detect_model_from_name`) — только если 1–4 пусты
6. `None` → resolver fallback GLM-5.2 + WARNING в stderr

## Тесты

`tests/test_backfill_model_detection.py` (герметичный каталог-кэш через
`CLOUDRU_PRICES_CACHE`):

- Pi-подобный артефакт (`results`+`summary`, имя `*_ds41flash_*`) → ставки DeepSeek,
  `(unknown …` в выводе отсутствует;
- `_detect_model_from_name` / `_detect_model`: `ds41flash`→DeepSeek, `giga35`/`gigachat35`
  →GigaChat 3.5;
- явное поле `model` приоритетнее имени файла;
- `per-task model` используется;
- неизвестное имя → fallback 990.64 ₽ **и** `WARNING` в stderr.

## Риски

- **Ложное срабатывание токена.** Токен `giga35`/`ds41flash` — достаточно специфичны;
  проверка идёт по стему имени. Тест на приоритет полей страхует от перезаписи явных
  данных.
- **Нетокенные семейства** (qwen36/oss120b/glm52/glm53/gigachat3pro) остаются на fallback —
  осознанно вне scope; для GLM-5.2 fallback численно верен.
