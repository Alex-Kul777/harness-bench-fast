# Proposal: fix-artifact-metadata

## Проблема

Артефакты прогонов записывают неполную и/или неверную метаданных-шапку (causes 3+5,
recording side), из-за чего результат нельзя надёжно интерпретировать и сравнивать:

- `run_openclaw_bench.py` хардкодит `task_set_version = "0.16.0"` **для всех** волн.
  Прогоны waves 17–19 (задачи 392–471) записываются как `0.16.0`, хотя эти задачи
  принадлежат task-set v0.17.0/v0.18.0/v0.19.x — сравнение и резюм ломаются
  («resume rejects a different task-set version»).
- `run_pi_bench.py` и `run_hermes_bench.py` не пишут метаданных-шапку вовсе:
  нет top-level `harness`, `harness_version`, `thinking`, `task_set_version`, `model`.
- Reasoning level не сохраняется: артефакт без уровня невоспроизводим (README:
  «a result without it is not reproducible»).

## Решение

Ввести единый контракт метаданных артефакта (top-level поля, без переименования):
`harness` (str), `harness_version` (str; отсутствует только если реально неизвестна),
`thinking` (str — reasoning level, либо `"default"`, если не задан),
`task_set_version` (str — **корректная для волны**), `model` (str).

- Все три раннера всегда пишут `harness` / `thinking` / `task_set_version` / `model`.
- `thinking` = эффективный reasoning level (`"default"`, если не задан).
- `task_set_version` вычисляется из задач прогона (не константа): waves 17–19
  (392–471) больше НЕ `"0.16.0"`, Light (1–391) остаётся `"0.16.0"`.
- `harness_version` пишется, если известна (флаг → env → best-effort autodetect);
  иначе поле отсутствует.

## Что входит в scope

- `harness_bench/artifact_metadata.py` — helper: `normalize_thinking()`,
  `task_set_version_for_tasks()`, `resolve_harness_version()`.
- Патч `_write_results()` в `run_openclaw_bench.py`, `run_pi_bench.py`,
  `run_hermes_bench.py` (только метаданные; pass/fail и ₽-аккаунтинг не трогаются).
- Тесты `tests/test_artifact_metadata.py`.
- OpenSpec ADDED-блок для `benchmark-runs`.

## Что НЕ входит в scope

- Изменение методологии pass/fail верификации.
- Изменение формулы стоимости (это `fix-runner-cost-rates`).
- Правка генераторов (`build_fork_*.py`), `scripts/backfill_cost_rub.py`,
  `harness_bench/cost_resolver.py` — запрещено write-scope.
- Пересчёт/бэкфилл уже закоммиченных артефактов (отдельная задача).
- Commit / push в main.

## Ссылки

- Frozen contract: top-level artifact fields (harness, harness_version, thinking,
  task_set_version, model) — имена не переименовывать.
- Причина: causes 3+5 (recording side).
