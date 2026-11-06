# add-fork-capability-sample-view — proposal

## Why

Cost-bounded capability sample (ADR-0003: 25% = 20 задач Medium) не виден на сайте:
файлы `pi_sample_*` исключаются генератором (keyword `sample`), отдельного вида нет.
Owner попросил опубликовать сэмпл как отдельный сюжет (аналог Light Shot List).

## What Changes

- Манифест сэмпла `docs/fork-sample-manifest.json` (20 задач, бэнды, правило) — источник правды.
- Генератор `scripts/build_fork_pages.py` собирает сэмпл из артефактов и пишет
  `docs/fork-sample-results.json` + статическую страницу `docs/fork-sample.html`.
- Ссылка на вид добавляется в шапку `docs/fork-medium90.html`.
- **long помечается `invalid`** (`timeout 2400 < wave floor 7200`), не как обычный fail.

Не **BREAKING**: Medium-вид не меняется.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `result-reporting` — добавляется требование «Вид capability-сэмпла».

## Out of scope

- Повторный прогон long с флором 7200 (владелец решит позже).
- Изменение Medium-вида/детализации.

## Impact

- `scripts/build_fork_pages.py`; `docs/fork-sample-manifest.json`, `docs/fork-sample-results.json`,
  `docs/fork-sample.html`; ссылка в `docs/fork-medium90.html`.

## Tracking

- Workboard: `c84277ff` (board project-a)
- Epic: #431
