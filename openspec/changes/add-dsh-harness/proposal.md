# add-dsh-harness

## Why

Форк умеет гонять бенчмарк через Pi, OpenClaw и Hermes, но не через официальный
harness DeepSeek AI — `dsh` (`@deepseek-ai/dsh`, v0.2.2-rc.1). Это единственный
харнесс, который сами авторы модели поставляют для агентных задач, поэтому его
отсутствие в матрице «модель × харнесс» оставляет слепое пятно: мы не знаем,
как DeepSeek-V4.1-Flash показывает себя в «родной» обвязке. Рабочая headless-команда
проверена вживую, а формат вывода (`--json` → NDJSON) и место usage
(`status.step_end.usage`) уже разведаны — не хватает раннера, регистрации харнесса
в форк-метаданных и спеки.

## What Changes

- **Новый раннер `run_dsh_bench.py`** — запускает `dsh --profile headless
  --patch <patch.yml> --permission-mode workspace-write --json '<task>'` в изолированном
  workspace с `DSH_HOME` и `DSH_BENCH_API_KEY` (ключ из `resolve_bench_api_key()`);
  переиспользует хелперы форка (`artifact_metadata`, `resolve_model_rates`,
  `effective_task_timeout`, checkpoint/`--fresh`, `--tasks`/`--shot-list`/`--concurrency`).
- **Чистые хелперы** — `build_headless_command(...)`, `build_provider_patch(...)`,
  `parse_dsh_jsonl(text) -> dict`; `--thinking <level>` инжектится в провайдер-роут
  патча (`none`/`off` → `off`); `--permission-mode` по умолчанию `workspace-write`.
- **Регистрация харнесса в форке** — `scripts/fork_metadata.py`: `HARNESS_PREFIXES`
  получает `("dsh_", "DeepSeek Harness")`, плюс регресс-тест на `classify_harness` /
  `resolve_stem` для стема `dsh_shotlist_ds41flash_...`.
- **Регресс-тест раннера** — `tests/test_runner_dsh_stream_json.py` на команду,
  патч и парсер (без секрета).
- **OpenSpec-дельта `benchmark-runs`** — раннер, источник usage, регистрация харнесса
  и artifact-шапка.

## Capabilities

### New Capabilities

_(нет)_

### Modified Capabilities

- `benchmark-runs`: ADDED «Раннер DeepSeek Harness (dsh)», «Usage из `status.step_end`»,
  «Регистрация харнесса dsh в форк-метаданных», «Artifact-шапка прогона dsh».

## Impact

- Новые файлы: `run_dsh_bench.py`, `tests/test_runner_dsh_stream_json.py`,
  `openspec/changes/add-dsh-harness/*`.
- Изменяется: `scripts/fork_metadata.py` (`HARNESS_PREFIXES`), `tests/test_fork_publish_orchestrator.py`
  (регресс-тест классификации).
- Никакие существующие артефакты `results/*.json` не меняются; чужие top-level
  `artifact_metadata` не трогаются.
- **Out of scope:** публикация страниц (оркестратор), таблицы/колонки, смысл метрик,
  upstream-строки README; поддержка `dsh` в других раннерах; изменение схема версий задач.
