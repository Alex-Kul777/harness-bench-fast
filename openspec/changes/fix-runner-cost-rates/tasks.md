# Tasks: fix-runner-cost-rates

- [ ] Написать `harness_bench/cost_resolver.py` с `resolve_model_rates()`
- [ ] Патч `run_openclaw_bench.py`: убрать хардкод, использовать resolver
- [ ] Патч `run_pi_bench.py`: убрать хардкод, использовать resolver
- [ ] Патч `run_hermes_bench.py`: убрать хардкод, использовать resolver
- [ ] Написать тесты `tests/test_runner_cost_rates.py`
- [ ] Написать `scripts/backfill_cost_rub.py`
- [ ] Запустить backfill на committed артефактах worktree
- [ ] QA: `validate --all --strict` == 0
- [ ] QA: `pytest tests/ -q` green
- [ ] QA: `run_openclaw_bench.py --help` работает
