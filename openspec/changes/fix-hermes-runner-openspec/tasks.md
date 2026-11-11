# Tasks: fix-hermes-runner-openspec

- [ ] Шапка метаданных Hermes через `harness_bench.artifact_metadata` (harness/model/thinking/task_set_version/harness_version)
- [ ] Уровень `thinking` = `--thinking`/`--thinking-off`→`none`/`default`
- [ ] Ставки модели через `resolve_model_rates` + `compute_cost_rub` (убрать хардкод GLM-5.2)
- [ ] Cache/reasoning бакеты в `summary` + вывод `max(total-input-output,0)` один раз + cache в стоимости
- [ ] `_write_status` принимает модель прогона
- [ ] Флаг `--thinking <level>` → `hermes chat --reasoning <level>`; `--thinking-off` алиас
- [ ] `harness_version` autodetect: `hermes --version`
- [ ] Не ломать memory-задачи 222–253 (без `--ignore-rules`) и `--provider custom`
- [ ] Написать регресс-тест `tests/test_runner_hermes_metadata.py` (зафиксировать RED→GREEN)
- [ ] QA: `python3 -m pytest tests/test_runner_hermes_metadata.py -q` — зелёный
- [ ] QA: `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
- [ ] QA: `python3 scripts/build_fork_results.py --check` == 0 (доки не регенерировать)
- [ ] QA: `python3 -c "import ast;ast.parse(open('run_hermes_bench.py').read())"` — OK
- [ ] QA: ручная проверка `--help` и dry-run сборки команды `hermes chat --reasoning <level>`
