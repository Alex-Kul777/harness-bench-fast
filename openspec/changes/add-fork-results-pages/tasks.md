# add-fork-results-pages — tasks

## 1. Реестр волн (build_fork_results.py)

- [ ] 1.1 Зарегистрировать umbrella-suite `Medium (392–471)`: include-regex для имён long/reflect/feasibility-прогонов, display-name + sort-order
- [ ] 1.2 Добавить classifier-ветки (harness/model) под новые имена
- [ ] 1.3 `python3 scripts/build_fork_results.py --check` → 0; `--lint` → 0

## 2. Генератор данных (build_fork_pages.py)

- [ ] 2.1 Сканировать `results/` (checkout + родитель, de-dup по имени), читать top-level `summary`
- [ ] 2.2 Сводить по волнам long/reflect/feasibility; считать `{passed,total}`, usage (seconds/steps/tokens/cost) и 95% Wilson
- [ ] 2.3 Писать `docs/fork-medium90-results.json` по замороженной в design.md схеме
- [ ] 2.4 Поддержать `--check` (exit 1 при устаревшем JSON) и `--json`/`--out`

## 3. Страница (docs/fork-medium90.html + docs/fork-results.js)

- [ ] 3.1 Статическая страница: header/бренд как у upstream, suite-switch, search
- [ ] 3.2 Матрица **Harness × Wave** + per-config таблица с 95% Wilson
- [ ] 3.3 Рендер из `fork-medium90-results.json`; порядок колонок/формулировки как upstream
- [ ] 3.4 Страница открывается локально и рендерит реальные данные

## 4. Публикация

- [ ] 4.1 Включить GitHub Pages форка (`main` / `/docs`)
- [ ] 4.2 Проверить, что страница отдаётся по `https://alex-kul777.github.io/harness-bench-fast/fork-medium90.html`

## 5. QA / верификация

- [ ] 5.1 `python3 scripts/build_fork_results.py --lint` → 0; negative-тест (удалить колонку → ненулевой код → вернуть)
- [ ] 5.2 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [ ] 5.3 Данные на странице совпадают с `results/*.json` (сверка счётчиков)
