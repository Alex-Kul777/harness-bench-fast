# fix-medium-sample-columns

## Why

Таблица `docs/fork.html#medium-sample` не выполняет требования спеки `result-reporting`,
которые уже действуют для остальных таблиц форка. Двухосевое ревью (`ask-matt` →
`code-review-two-axis`) зафиксировало:

1. `Profile` — нет суффикса даты `(YYYY-MM-DD)` (spec:332).
2. `Model` — нет уровня ризонинга и провайдера `(cloud.ru)` (spec:397).
3. `Harness` — нет версии харнеса, хотя артефакты её пишут (`OpenClaw 2026.10.9 (8b18b55)`)
   (spec:414).
4. Нет канонической колонки `Steps` (spec:10/15).

Причина: `sample_rows()` в `scripts/build_fork_home.py` строит строки «сырыми»
(`r.get(...)`), не прогоняя их через `_with_date` / `_with_reasoning` / `_with_version`,
которые уже применяются к строкам `#medium`. Гейты это не ловят: у `build_fork_home.py`
нет `--lint`, `--check` лишь сверяет байты, `build_fork_results.py --lint` смотрит только
`FORK.md` / `docs/fork-results.md`, а pytest семпл-строки не рендерит.

## What Changes

- **Семпл-таб использует канонические метаданные:** `sample_rows()` применяет `_with_date`
  (дата из `sources` / имени файла; пилот — дата манифеста), `_with_reasoning` + провайдер
  `(cloud.ru)` и `_with_version`; добавляется колонка `Steps`.
- **Версия харнеса доходит до строк:** `scripts/build_fork_pages.py` пропагирует
  `harness_version` в `docs/fork-medium90-results.json`.
- **Пилоты:** `Time` / `Tokens (cost)` читаются из манифеста / `sources`, а не хардкодятся `—`.
- **Провайдер в спеке:** формат `Model` расширяется до `модель (провайдер) (уровень)`.
- **Standards-фиксы (из ревью):** единый `DASH` в `fork_metadata.py`; `raise ValueError`
  вместо `assert` при чтении внешних JSON; дедуп near-identical блоков в
  `build_medium90_data.py`; guard от пустого пилот-манифеста.
- **Тесты-сторожа** на дату / уровень / провайдер / версию / `Steps` и паритет RU/EN.

## Capabilities

### New Capabilities

_(нет)_

### Modified Capabilities

- `result-reporting`:
  - MODIFIED «Уровень ризонинга в колонке Model» — формат включает провайдера.
  - ADDED «Канонические колонки и метаданные семпл-таба».

## Impact

- Изменяются: `scripts/build_fork_home.py`, `scripts/build_fork_pages.py`,
  `scripts/build_medium90_data.py`, `scripts/fork_metadata.py`; регенерируемые `docs/`.
- Тесты: новые в `tests/`.
- **Out of scope:** схема колонок прочих таблиц и upstream-строк; смысл метрик; сам
  Pages-workflow (`.github/workflows/pages.yml` уже существует); изменение формата
  `#medium` (он уже соответствует спеке).

## Workboard

- Card: `fea37a42-9387-4416-8b0c-67d6c9a1673a` (board `project-a`).
