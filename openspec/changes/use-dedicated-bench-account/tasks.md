# Tasks: use-dedicated-bench-account

- [ ] Общий helper `harness_bench/bench_credentials.py:resolve_bench_api_key()`: приоритет `CLOUD_RU_BENCH_API_KEY` → `CLOUD_RU_KAP_HERMES` (env, затем `~/.hermes/.env`) → `CLOUD_RU_API_KEY`, stderr-NOTE
- [ ] `run_pi_bench.py`: резолвинг ключа через helper (убрать ручной блок `CLOUD_RU_API_KEY`/Hermes .env)
- [ ] `run_hermes_bench.py`: резолвинг ключа через helper; `OPENAI_API_KEY` из резолвера (не production-first)
- [ ] `run_openclaw_bench.py`: прокинуть резолвнутый ключ в окружение `openclaw agent exec` (минимально, не ломая конфиг-провайдер)
- [ ] Записать источник ключа в артефакт: `summary.bench_credential` во всех трёх раннерах
- [ ] Production `CLOUD_RU_API_KEY` SHALL NOT использоваться бенчем при наличии `CLOUD_RU_BENCH_API_KEY`
- [ ] Написать регресс-тест `tests/test_bench_credentials.py` (приоритет, fallback, NOTE; RED→GREEN)
- [ ] QA: `python3 -m pytest tests/test_bench_credentials.py -q` — зелёный
- [ ] QA: существующие runner-тесты (`tests/test_runner_*.py`) — зелёные
- [ ] QA: `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
- [ ] QA: `python3 scripts/build_fork_results.py --check` == 0 (доки не регенерировать)
- [ ] QA: `python3 -c "import ast;ast.parse(open('run_pi_bench.py').read())"` и то же для Hermes/OpenClaw — OK
