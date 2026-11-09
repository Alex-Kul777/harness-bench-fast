# Tasks: fix-cost-model-detection

- [ ] Добавить `_FILENAME_MODEL_TOKENS` + `_detect_model_from_name` в `scripts/backfill_cost_rub.py`
- [ ] Расширить `_detect_model(data, name="")`: поля → имя файла (только если поля пусты)
- [ ] Прокинуть `path.name` из `_recompute_file` в `_detect_model`
- [ ] Обновить docstring модуля (детекция из имени файла как last resort)
- [ ] Написать `tests/test_backfill_model_detection.py`
- [ ] QA: `python3 -m pytest tests/test_backfill_model_detection.py -q` — green
- [ ] QA: `python3 scripts/backfill_cost_rub.py results/ --dry-run` — `pi_*_ds41flash_*` резолвятся в DeepSeek (не `(unknown → fallback)`); `giga35` → GigaChat 3.5
- [ ] QA: `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` — exit 0
- [ ] (вне change) прогнать бэкфилл без `--dry-run` и закоммитить пересчитанные `results/*.json`
