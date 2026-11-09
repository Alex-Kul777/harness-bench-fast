# Tasks: fix-artifact-metadata

- [x] Добавить `harness_bench/artifact_metadata.py` (`normalize_thinking`, `task_set_version_for_tasks`, `resolve_harness_version`)
- [x] Патч `run_openclaw_bench.py`: `_write_results` пишет harness/harness_version/thinking/task_set_version/model
- [x] Патч `run_pi_bench.py`: `_write_results` пишет шапку; прокинуть thinking/model/task_ids
- [x] Патч `run_hermes_bench.py`: `_write_results` пишет шапку; прокинуть thinking/model/task_ids
- [x] Написать тесты `tests/test_artifact_metadata.py`
- [x] QA: `python3 -m pytest tests/test_artifact_metadata.py -q` green
- [x] QA: `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
