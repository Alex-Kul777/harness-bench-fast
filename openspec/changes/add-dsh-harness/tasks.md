# add-dsh-harness — tasks

## 1. Раннер
- [x] 1.1 `run_dsh_bench.py`: хелперы `build_headless_command`, `build_provider_patch`, `parse_dsh_jsonl`
- [x] 1.2 `run_one_task`: изолированный workspace + `DSH_HOME`/`DSH_BENCH_API_KEY`, temp-patch
- [x] 1.3 `passed` = exit 0 И `final.reason.kind == 'completed'` И верификатор
- [x] 1.4 CLI: `--tasks` (space/comma), `--pilot`, `--failed-only`, `--all`, `--shot-list`,
      `--suite`, `--concurrency`, `--timeout`, `--json-output`, `--status-file`, `--fresh`,
      `--rerun-on-fail`, `--keep`, `--harness-version`
- [x] 1.5 `--thinking` (none|off|minimal|low|medium|high|max|ultra) → `reasoning` провайдер-роута
- [x] 1.6 `--permission-mode` по умолчанию `workspace-write`
- [x] 1.7 Артефакт: шапка `artifact_metadata(harness="dsh", ...)`, summary с токенами/стоимостью/`bench_credential`

## 2. Регистрация харнесса в форке
- [x] 2.1 `scripts/fork_metadata.py`: `HARNESS_PREFIXES` += `("dsh_", "DeepSeek Harness")`
- [x] 2.2 Регресс-тест `classify_harness` / `resolve_stem` для `dsh_shotlist_ds41flash_...`

## 3. Тесты раннера
- [x] 3.1 `tests/test_runner_dsh_stream_json.py`: команда (без секрета), патч (bare id + reasoning), парсер NDJSON

## 4. Спека
- [x] 4.1 Дельта `benchmark-runs` (ADDED: раннер, usage, регистрация, artifact-шапка)

## 5. QA / верификация
- [x] 5.1 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
- [x] 5.2 `pytest tests/test_runner_dsh_stream_json.py tests/test_fork_publish_orchestrator.py` — зелёные
- [x] 5.3 `python3 scripts/build_fork_results.py --check` == 0
- [x] 5.4 Живой smoke на `deepseek-ai/DeepSeek-V4.1-Flash` (1–2 задачи), artifact summary получен
