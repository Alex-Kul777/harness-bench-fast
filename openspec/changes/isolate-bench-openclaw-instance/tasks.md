# Tasks: isolate-bench-openclaw-instance

> Реализация НЕ начинается до ревью proposal.md (OpenSpec: propose → review → apply).

## Диагностика (сделано)
- [x] Понять вызов: `agent exec` читает ambient-конфиг оператора + плагины/MCP
      (`docs/cli/agent.md`)
- [x] Подтвердить, что ambient-конфиг содержит plugins/MCP/skills/memory
- [x] Собрать `bench/openclaw.bench.json` (только Cloud.ru провайдер + модели, env-ключ)
- [x] Смоук изолированного вызова (env-конфиг → provider + usage OK), 2× зелёный
- [x] Решающий тест: OC-нога `task_403` на чистом инстансе (в фоне; см. статус)

## Реализация
- [ ] `run_openclaw_bench.py`: добавить `--config <repo>/bench/openclaw.bench.json` в argv `agent exec`
- [ ] `run_openclaw_bench.py`: убедиться, что `CLOUD_RU_BENCH_API_KEY` попадает в env вызова
- [ ] `bench/README.md`: назначение/запуск/что изолировано
- [ ] `bench/openclaw.bench.json`: финализировать (модели, без plugins/mcp/skills)

## QA
- [ ] RED→GREEN: `tests/test_oc_bench_isolation.py` (argv содержит `--config`; конфиг без plugins/mcp/skills)
- [ ] `python3 -m pytest tests/test_oc_bench_isolation.py -q` → green
- [ ] Смоук: `agent exec --config bench/openclaw.bench.json …` → провайдер резолвится, usage есть
- [ ] Решающий: OC-нога длинной задачи на чистом инстансе больше не крашится (или краш воспроизводится → эскалируем в продукт)
- [ ] `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [ ] `python3 scripts/build_fork_results.py --check` → 0

## Архив
- [ ] `openspec archive isolate-bench-openclaw-instance` после зелёного QA
