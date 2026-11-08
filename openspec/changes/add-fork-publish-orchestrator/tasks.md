# add-fork-publish-orchestrator — tasks

## 1. Метаданные
- [x] 1.1 `scripts/fork_metadata.py`: перенести `HARNESS_PREFIXES`, `MODEL_TOKENS`, `THINKING_LEVEL_RE`, резолвер stem→(harness, model, reasoning level), `collect_paths()`
- [x] 1.2 Перевести на импорт `build_fork_pages.py`, `build_fork_home.py`, `build_fork_results.py`; удалить дубли
- [x] 1.3 Parity: `--check` всех генераторов = 0; страницы байт-в-байт для существующих прогонов

## 2. Оркестратор
- [x] 2.1 `scripts/publish_fork.py`: генераторы в порядке, RU+EN
- [x] 2.2 Гейт `--check`/`--lint` на чистом `git archive` (без sibling `../results/`)
- [x] 2.3 Конкурентный гард: вынос/возврат свежих `../results/*.json`; стоп при активном `run_bench`
- [x] 2.4 Коммит явными путями; push в `main` только при зелёных проверках (fail-closed); проверка Pages (poll 200 + cache-buster)
- [x] 2.5 Флаги `--no-publish`/`--no-commit`/`--no-push`/`--dry-run`
- [x] 2.6 Hard-fail: нерезолвимый stem; неполный прогон (нет top-level `summary` / in-flight)

## 3. Автозапуск
- [ ] 3.1 `run_pi_bench.py` / `run_openclaw_bench.py`: `--publish` (default ON) + `--no-publish`

## 4. Спека
- [ ] 4.1 Дельта `result-reporting` (3 ADDED: оркестратор, метаданные, гард)
- [ ] 4.2 Дельта `benchmark-runs` (1 ADDED: автозапуск)

## 5. QA / верификация (QA-задача для user-facing результата)
- [ ] 5.1 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [ ] 5.2 `--check`/`--lint` RU+EN = 0; то же на чистом `git archive` дереве
- [x] 5.3 Тест: hard-fail на нерезолвимый stem (публикация не идёт)
- [x] 5.4 Тест: incomplete-run guard (нет `summary` → отказ)
- [x] 5.5 Тест: parity — дедуп метаданных не меняет опубликованные страницы
- [ ] 5.6 Live: после публикации страница 200, строка и detail-страница на месте
