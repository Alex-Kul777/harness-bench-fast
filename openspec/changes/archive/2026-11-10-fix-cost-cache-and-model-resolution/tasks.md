# Tasks: fix-cost-cache-and-model-resolution

- [x] Написать тесты `tests/test_cost_cache_bucket.py` и `tests/test_cost_filename_hints.py` (red)
- [x] Патч `run_openclaw_bench.py::_write_results`: derivation cache-read
- [x] Патч `scripts/backfill_cost_rub.py`: derivation cache-read + передача filename
- [x] `harness_bench/cost_resolver.py`: карта подсказок имени файла + `filename=` в `resolve_model_rates`
- [x] Прогнать тесты (green) + смежные cost-тесты
- [x] Backfill committed артефактов `results/`
- [x] Перегенерировать `docs/fork-*` (`build_fork_pages`, `build_fork_results`, `build_fork_home`)
- [x] QA: `openspec validate --all --strict` == 0
- [x] QA: `python3 scripts/build_fork_results.py --check` == 0
- [x] QA: свидетельства 572.89 ₽ и 62.12 ₽
