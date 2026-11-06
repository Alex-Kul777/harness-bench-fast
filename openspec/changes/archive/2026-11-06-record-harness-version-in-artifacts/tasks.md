# record-harness-version-in-artifacts — tasks

- [x] 1.1 `set_results_json_harness_version` + `_RESULTS_JSON_HARNESS_VERSION` в runner.py
- [x] 1.2 `harness_version` в `results_to_payload` (когда задано)
- [x] 1.3 CLI `--harness-version` + env-fallback в `__main__.py`; сброс в `finally`
- [x] 2.1 Delta `benchmark-runs`: ADDED «Версия харнеса в артефакте»
- [x] 3.1 Смоук: payload с `harness_version`; `--help` показывает флаг; env-fallback
- [x] 3.2 Целевые тесты раннера зелёные (кроме предсуществующих langgraph-фейлов)
- [x] 3.3 `openspec validate --all --strict` → 0
