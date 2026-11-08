# add-fork-publish-orchestrator

## Why

Публикация форк-слоя сегодня — ручная цепочка: регенерировать три генератора, вручную
дополнить классификатор модели **в каждом** из них (дубли `HARNESS_PREFIXES` /
`MODEL_TOKENS` / `THINKING_LEVEL_RE`), собрать RU+EN, прогнать `--check`/`--lint` на чистом
дереве, закоммитить, задеплоить Pages и проверить live. Между «прогон завершён» и «строка
на странице» связи нет: раннеры только пишут `results/*.json` и останавливаются — а
владелец ожидает, что публикация идёт сразу после бенчмарка. Забытый токен в одном из
генераторов молча даёт пустые ячейки на опубликованной странице. Решения зафиксированы в
`docs/adr/0005-fork-publish-orchestrator.md` (grilling: `ask-matt` → `grill-with-docs`).

## What Changes

- **Новый общий модуль `scripts/fork_metadata.py`** — единый источник `HARNESS_PREFIXES`,
  `MODEL_TOKENS`, `THINKING_LEVEL_RE`, резолвер stem→(harness, model, reasoning level) и
  `collect_paths()`; три генератора и оркестратор импортируют его, дубли удаляются.
- **Новый оркестратор `scripts/publish_fork.py`** — публикация одной командой: генераторы в
  порядке, RU+EN, гейт `--check`/`--lint` на чистом `git archive`, конкурентный гард
  (изоляция свежих `../results/*.json` и возврат), коммит, push в `main` при зелёных
  проверках (fail-closed), проверка Pages.
- **Автозапуск:** флаги раннеров `--publish` (по умолчанию ВКЛ) и `--no-publish`; по
  завершении прогона вызывается оркестратор.
- **Hard-fail:** нерезолвимый stem и неполный прогон (нет top-level `summary` / in-flight
  маркеры) → ненулевой код, публикация не идёт.

## Capabilities

### New Capabilities

_(нет)_

### Modified Capabilities

- `result-reporting`: ADDED «Оркестратор публикации», «Единый источник метаданных стема»,
  «Конкурентный гард публикации».
- `benchmark-runs`: ADDED «Автозапуск публикации после прогона».

## Impact

- Новые файлы: `scripts/fork_metadata.py`, `scripts/publish_fork.py`, тесты.
- Изменяются: `scripts/build_fork_pages.py`, `scripts/build_fork_home.py`,
  `scripts/build_fork_results.py` (импорт метаданных); `run_pi_bench.py`,
  `run_openclaw_bench.py` (флаг `--publish`).
- Регенерируемые `docs/` должны остаться без изменений для существующих прогонов
  (parity-проверка).
- **Out of scope:** схема публикуемых таблиц/колонок; upstream-строки; смысл метрик;
  сам Pages-workflow (`.github/workflows/pages.yml` уже существует); изменение правила
  версионирования ассетов.

## Workboard

- Card: `f1d8c5f9-6083-4f1a-805c-837f46a7f977` (board `project-a`).
