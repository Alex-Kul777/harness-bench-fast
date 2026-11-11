# Tasks: fix-hermes-cli-compat

- [x] Команда: убрать `-v`, добавить `--format stream-json`, `--base-url`, `--api-key` (custom)
- [x] Bare model id для `--provider custom` (`_bare_model_id`, срезать `custom-foundation-models-api-cloud-ru/`)
- [x] Разбор токенов/`session_id` из stream-json `result` (`_parse_stream_json`); fallback → 0 + ошибка
- [x] Сохранить `agent_*`-поля, `summary` и top-level `artifact_metadata` без изменений
- [x] `--ignore-rules` — для всех задач, кроме memory 222–253
- [x] Регресс-тест `tests/test_runner_hermes_stream_json.py`
- [x] OpenSpec-дельта `benchmark-runs` (ADDED: флаги, bare model, stream-json usage)
- [x] QA: `python3 -m pytest tests/test_runner_hermes_stream_json.py tests/test_runner_hermes_metadata.py -q` — зелёный
- [x] QA: `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
- [x] QA: `python3 scripts/build_fork_results.py --check` == 0 (доки не регенерировать)
- [x] QA: `python3 -c "import ast; ast.parse(open('run_hermes_bench.py').read())"` — OK
- [ ] QA: ручный прогон shot-list на Hermes 0.23.1 (вне этого worktree; не блокирует change)
