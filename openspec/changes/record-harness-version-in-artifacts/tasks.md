# record-harness-version-in-artifacts — tasks

- [ ] 1.1 `set_results_json_harness_version` + `_RESULTS_JSON_HARNESS_VERSION` в runner.py
- [ ] 1.2 `harness_version` в `results_to_payload` (когда задано)
- [ ] 1.3 CLI `--harness-version` + env-fallback в `__main__.py`; сброс в `finally`
- [ ] 2.1 Delta `benchmark-runs`: ADDED «Версия харнеса в артефакте»
- [ ] 3.1 Смоук: payload с `harness_version`; `--help` показывает флаг; env-fallback
- [ ] 3.2 Целевые тесты раннера зелёные (кроме предсуществующих langgraph-фейлов)
- [ ] 3.3 `openspec validate --all --strict` → 0
