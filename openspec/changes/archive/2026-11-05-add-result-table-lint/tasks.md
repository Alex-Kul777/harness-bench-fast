# add-result-table-lint — tasks

## 1. Реализация

- [x] 1.1 Добавить режим `--lint` в `scripts/build_fork_results.py`: сканировать `FORK.md` и `docs/fork-results.md`, находить результатные таблицы, проверять канонические колонки
- [x] 1.2 Вывести имя файла + отсутствующие колонки и вернуть ненулевой код при провале

## 2. Интеграция

- [x] 2.1 Добавить шаг `--lint` в `.github/workflows/openspec-validate.yml`

## 3. QA / верификация

- [x] 3.1 `python3 scripts/build_fork_results.py --lint` возвращает `0` на текущих файлах
- [x] 3.2 На искусственно испорченной таблице `--lint` возвращает ненулевой код
- [x] 3.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` возвращает `0`
