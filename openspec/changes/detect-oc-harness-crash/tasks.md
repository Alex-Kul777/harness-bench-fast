# Tasks: detect-oc-harness-crash

> Реализация НЕ начинается до ревью proposal.md (OpenSpec: propose → review → apply).

## Диагностика (сделано)
- [x] Red: воспроизвести краш OC-ноги 2/2 (`task_403`, DS-V4.1-Flash, off, timeout 7200)
- [x] Собрать полный stderr: `MaxListenersExceededWarning` на `[Socket]`, `403 … sensitive information`, `Provider returned an incomplete or malformed tool call`
- [x] Гипотеза: пред-диспатч rejection → ретраи по keep-alive сокету → лик `connect`-листенеров → `exit=1`, 0 usage
- [x] Диагноз-док + минимальный репро (`docs/research/2026-11-17-openclaw-exec-crash-diagnosis.md`, `scripts/repro_oc_longtask_crash.sh`)

## Реализация
- [ ] `run_openclaw_bench.py`: константа `HARNESS_CRASH_MARKERS` + детектор `detect_harness_crash(stderr, returncode, usage, error)`
- [ ] `run_one_task`: проставлять `harness_error`/`harness_error_kind` в per-task запись
- [ ] `_write_results`: `summary.harness_errors`, `summary.harness_error_tasks`, `summary.comparable`
- [ ] Форк-страницы: рендер `invalid (harness error)` в строках и детализации

## QA
- [ ] RED→GREEN: `tests/test_oc_harness_crash_detection.py` (фикстура listener-leak + 0 usage → `harness_error: true`, `harness_errors=1`, `comparable=false`)
- [ ] Тест: обычный fail и контентный 403 с ненулевым usage НЕ помечаются крахом
- [ ] Тест обратной совместимости: старый артефакт → `harness_errors=0`, `comparable=true`
- [ ] `python3 -m pytest tests/test_oc_harness_crash_detection.py -q` → green
- [ ] `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [ ] `python3 scripts/build_fork_results.py --check` / `build_fork_pages.py --check` / `build_fork_home.py --check` → 0
- [ ] QA: перегенерировать форк-страницы, глазами проверить, что OC-краш-строка = `invalid`

## Архив
- [ ] `openspec archive detect-oc-harness-crash` после зелёного QA
