# fix-medium-sample-columns — tasks

## 1. Генератор семпл-таба

- [x] 1.1 `build_fork_home.py sample_rows()`: применять `_with_date` (дата из `sources`/имени файла; пилот — дата манифеста), `_with_reasoning` + провайдер `(cloud.ru)` к `Model`, `_with_version` к `Harness`
- [x] 1.2 Добавить колонку `Steps` в `SAMPLE_HEAD` и `_sample_rows_html` (значение из `usage.steps`/`summary.total_steps`, иначе `—`)
- [x] 1.3 `build_fork_pages.py`: пропагировать `harness_version` артефактов в строки `docs/fork-medium90-results.json`
- [x] 1.4 Пилот-строка: `Time`/`Tokens (cost)` читать из манифеста/`sources` вместо хардкода `—`

## 2. Standards (по ревью)

- [x] 2.1 Единый `DASH` в `fork_metadata.py`; заменить хардкод `"\u2014"` в `build_fork_pages.py`
- [x] 2.2 `build_medium90_data.py`: `raise ValueError` вместо `assert`; чтение внешних JSON в `try/except`
- [x] 2.3 `build_medium90_data.py`: извлечь дублирующиеся блоки в `_fresh_medium90_row(...)`
- [x] 2.4 `build_fork_home.py`: guard от пустого пилот-манифеста (не выдавать `0/0`)

## 3. Тесты-сторожа

- [x] 3.1 Тест: семпл-строка содержит дату в `Profile`, уровень+провайдер в `Model`, версию в `Harness`, колонку `Steps`
- [x] 3.2 Тест: пилот `Time`/`Tokens` берутся из манифеста (не хардкод); `—` только при отсутствии
- [x] 3.3 Тест: паритет строк RU/EN семпл-таба

## 4. Verify / QA (для user-facing результата)

- [x] 4.1 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
- [x] 4.2 `python3 -m pytest tests/ -q` — целевые тесты зелёные (env-падения отделить)
- [x] 4.3 `build_fork_home.py --check`, `build_fork_results.py --check/--lint` == 0 на чистом дереве
- [x] 4.4 Live: `docs/fork.html#medium-sample` показывает дату / уровень+провайдер / версию / `Steps`

## 5. Archive / land

- [x] 5.1 `openspec archive fix-medium-sample-columns` (после всех `[x]`)
- [x] 5.2 push `main` (ff) + Pages poll
