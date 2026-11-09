# Proposal: fix-cost-model-detection

## Why

Скрипт пересчёта ₽-стоимости `scripts/backfill_cost_rub.py` определяет модель артефакта
функцией `_detect_model`, которая смотрит только поля `model`, `summary.model`,
`model` первой задачи и `command`. Артефакты Pi несут **только** `results` + `summary`
(проверено: `pi_shotlist_ds41flash.json`, `pi_medium_long_giga35_low_20261107.json` и др. —
`model=None`, `command=None`). Из-за этого детекция возвращает `None`, и
`harness_bench/cost_resolver.py` молча подставляет fallback GLM-5.2
(239.12/751.52/0/0) вместо реальных ставок модели: для DeepSeek-V4.1-Flash это
64.94/194.81/6.5/0, для GigaChat 3.5 Reasoning — 96.22/288.6/0/0.

Следствие (cause 4): завышенная ₽-стоимость в закоммиченных артефактах. На `results/`
до фикса 11 файлов `pi_*`/`wave19_full_ds41flash` получали fallback-ставки; напр.
`pi_shotlist_ds41flash.json` показывал 129.97 ₽ вместо корректных 34.50 ₽,
`wave19_full_ds41flash.json` — 3923.16 ₽ вместо 1045.25 ₽.

## What Changes

- `scripts/backfill_cost_rub.py`: `_detect_model(data, name="")` расширяется — после
  проверки всех полей (и только если они отсутствуют) модель выводится из **имени
  файла/семейства** по явной небольшой карте `_FILENAME_MODEL_TOKENS`:
  `*_ds41flash_*` → `custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash`;
  `*_giga35_*` / `*_gigachat35_*` → `ai-sage/GigaChat3.5-432B-A28B-Reasoning`.
- Приоритет сохраняется: явные поля выигрывают у имени файла (напр.
  `oc_shotlist_ds41flash.json` хранит поле `model=GLM-5.2` — остаётся как есть).
- Задокументированный fallback GLM-5.2 + WARNING в stderr сохраняются **только** для
  действительно неопределимых артефактов.
- Тесты `tests/test_backfill_model_detection.py`: Pi-подобный артефакт (только
  `results`+`summary`) резолвится в ставки DeepSeek (а не fallback);
  `*_ds41flash_*` → DeepSeek; `giga35`/`gigachat35` → GigaChat 3.5 Reasoning;
  неизвестное имя → fallback **с** предупреждением; поле-`model` приоритетнее имени.
- Публичный API `harness_bench/cost_resolver.py` (`resolve_model_rates`,
  `compute_cost_rub`) не меняется.

## Capabilities

### New Capabilities
- (нет)

### Modified Capabilities
- `benchmark-runs`: ADDED-требование «Детекция модели для расчёта ₽-стоимости
  артефакта» — детекция модели по полям с fallback на имя файла/семейство; ставки
  именно определённой модели; fallback GLM-5.2 + WARNING только для неопределимых.

## Impact

- Код: `scripts/backfill_cost_rub.py` (изменён), `harness_bench/cost_resolver.py` (без
  изменений — публичный API сохранён).
- Тесты: `tests/test_backfill_model_detection.py` (новый).
- Данные: `results/*.json` пересчитываются бэкфиллом (запись — вне этого change;
  здесь только детекция + dry-run-подтверждение).
- **Out of scope:** pass/fail-методология, схема артефактов, раннеры
  (`run_*_bench.py`), `scripts/build_fork_*.py`, расширение карты на прочие семейства
  (qwen36/oss120b/glm52/glm53/gigachat3pro остаются «неизвестными» → fallback),
  правка поля-`model` в `oc_shotlist_ds41flash.json` (данные, не детекция),
  git commit / push / merge.

## Workboard

- Card: не заводился (задача выдана субагенту через OpenSpec-change `fix-cost-model-detection`).
