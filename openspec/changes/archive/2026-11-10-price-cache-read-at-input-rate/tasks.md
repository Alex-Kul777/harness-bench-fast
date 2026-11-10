# Tasks: price-cache-read-at-input-rate

- [x] Написать тесты `tests/test_cost_cache_input_rate_policy.py` (red)
- [x] `harness_bench/cost_resolver.py`: cache-тариф отсутствует → входная ставка + NOTE
- [x] `run_openclaw_bench.py::_write_results`: явные `summary.total_cache_read_tokens`/`total_cache_write_tokens`
- [x] `scripts/backfill_cost_rub.py`: PREFER явные бакеты, иначе вывод, запись обратно
- [x] Прогнать cost-тесты (green) + смежные (52 passed, новые 8 green)
- [x] Backfill `results/` (явные бакеты + пересчёт ₽)
- [x] Перегенерировать `docs/fork-*` (`build_fork_pages`, `build_fork_results`, `build_fork_home`)
- [x] QA: `openspec validate --all --strict` == 0
- [x] QA: `build_fork_results.py --check/--lint`, `build_fork_pages.py --check`, `build_fork_home.py --check` == 0
- [x] QA: pytest green; свидетельства 8635.58 / 956.96 / 572.89 ₽
