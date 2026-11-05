# add-runner-suite-selector — design

## Context

См. `proposal.md` — Why. Фаза 0 (Epic #428) подтвердила: `TASK_SET_VERSION = 0.21.3`,
все новые суиты есть в `harness_bench.tasks.SUITES` (`long`/`reflect`/`feasibility`/
`general-hard`/`composite-hard`), верификаторы callable у 100% задач. Гэп — только
в CLI кастомных раннеров.

## Goals / Non-Goals

- **Goals:** прогнать волну одним флагом `--suite <name>`, без хардкода ID.
- **Non-Goals:** подбор timeout, scoring, запуск прогонов.

## Decisions

- **Источник имён — `harness_bench.tasks.SUITES`**, а не диапазоны в раннере:
  единый источник правды, волна не «расходится» при бампе task-set. Альтернатива
  (хардкод границ 412–431) отклонена как дублирование.
- **Один флаг `--suite` в оба раннера** с `choices=sorted(SUITES)`. `--all` у
  OpenClaw остаётся (обратная совместимость, = `default`).
- **Приоритет:** `--tasks` > `--suite` > `--pilot` > `--shot-list`/`--all`.
- **Ошибка на неизвестном имени:** argparse `choices` даёт ненулевой код до старта.

## Risks / Trade-offs

- [Upstream переименует суит] → имя берётся из `SUITES`, ошибка будет явной.
- [Раннер вне OpenSpec-репо (`openclaw-workspace`)] → спека описывает поведение,
  код живёт в workspace; связь фиксируется в `proposal.md`/ADR.

## Migration Plan

Добавить флаг, покрыть тестом. Откат — убрать флаг; поведение по умолчанию не менялось.

## Open Questions

Нет.
