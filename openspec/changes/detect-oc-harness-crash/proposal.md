# detect-oc-harness-crash

## Why

OC-нога на длинных/сложных задачах периодически падает **не из-за модели**, а из-за
краха харнесса `openclaw agent exec`. Воспроизведено 2/2 на
`task_403_binary_format_reverse` (DeepSeek-V4.1-Flash, `thinking=off`, `--timeout 7200`):

- прогон #1: 1 шаг, 2967 с → `MaxListenersExceededWarning: 11 connect listeners added
  to [Socket] (MaxListeners is 10)` + `Provider returned an incomplete or malformed tool call`;
- прогон #2: 14 шагов, 535 с → тот же warning + `403 Input text May contain sensitive
  information, please try again.`

Раннер видит `returncode != 0` и **0 usage** и записывает это как обычный `passed=false`
с `agent_total_tokens=0`. Из-за этого:

1. **pass-rate искажается**: крах харнесса учитывается как «модель не решила», хотя
   попытки не было;
2. **₽-учёт искажается**: 0 токенов → 0 ₽ → прогон выглядит «бесплатным fail»;
3. это корень уже открытых карточек про OC «0 usage» (`8f99e6e8`, `28e03383`).

Сам дефект живёт в продукте OpenClaw (вне репо); в этом репо мы можем **достоверно
детектировать** краш-инфраструктуру в артефакте и **не смешивать** её с провалом модели.

Диагноз: `docs/research/2026-11-17-openclaw-exec-crash-diagnosis.md` (ветка research,
навык `diagnosing-bugs`). Карточка Workboard: `3cae8a52`.

## What Changes

- **`run_openclaw_bench.run_one_task`**: распознаёт инфраструктурный краш по признакам
  (непустой `stderr` с маркерами `MaxListenersExceededWarning` / `EventEmitter memory
  leak` / `Use emitter.setMaxListeners`, ИЛИ `returncode != 0` при нулевом usage) и
  помечает per-task запись `harness_error: true` (+ `harness_error_kind`), сохраняя
  текст ошибки. Признак не влияет на `passed` в сторону «успеха».
- **`run_openclaw_bench._write_results`**: пишет в `summary` счётчик
  `harness_errors` и список `harness_error_tasks`; `total_tokens`/`estimated_cost_rub`
  остаются по факту (0), но прогон с любым `harness_error: true` помечается
  `comparable: false`.
- **result-reporting**: строки/задачи с `harness_error: true` показываются как
  `invalid (harness error)`, а не как обычный `fail`; такие прогоны SHALL NOT считаться
  сопоставимыми в pass-rate.
- **Регресс-тест** `tests/test_oc_harness_crash_detection.py`: фикстура конверта/статуса
  с `MaxListenersExceededWarning` и 0 usage → задача обязана получить `harness_error: true`,
  `summary.harness_errors = 1`, `comparable = false`.

## Capabilities

### New Capabilities

_(нет)_

### Modified Capabilities

- `benchmark-runs`: ADDED «Детекция инфраструктурного краха OC-раннера»,
  «Маркер `harness_error` в per-task и summary», «Несопоставимость прогона с крахом».
- `result-reporting`: ADDED «Отображение harness-краха как `invalid`, а не `fail`».

## Out of scope

- **Починка самого `openclaw agent exec`** (listener leak, обработка пред-диспатч
  rejection, guardrail Cloud.ru) — это продукт OpenClaw, вне репозитория; трекается
  карточкой `3cae8a52` + доком диагноза.
- Пересчёт/бэкфилл уже опубликованных артефактов (делается отдельным change-ом при
  необходимости).
- Изменение таймаутов/floors задач, смена модели или уровня ризонинга.
- Любые правки upstream-методологии.

## Impact

- `run_openclaw_bench.py` (детекция + summary-поля), `tests/test_oc_harness_crash_detection.py` (новый),
  `openspec/changes/detect-oc-harness-crash/*`, при реализации — генераторы форк-страниц
  (`scripts/build_fork_pages.py` / `build_fork_home.py`) для отображения `invalid`.
- Существующие `results/*.json` не переписываются; новые поля аддитивны.
- Ссылки: Workboard `3cae8a52`; диагноз `docs/research/2026-11-17-openclaw-exec-crash-diagnosis.md`.
