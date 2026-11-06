# result-reporting (delta)

## ADDED Requirements

### Requirement: Данные страницы результатов форка

Форк SHALL генерировать файл `docs/fork-medium90-results.json` из JSON-прогонов
(`results/`) скриптом `scripts/build_fork_pages.py` по замороженной схеме: строки
конфигураций с полями `harness`, `model`, `profile`, `runs`, `suites` (по волнам
long/reflect/feasibility), `usage`, `wilson`, `sources`.

#### Scenario: Свод по волнам

- **WHEN** запускается `python3 scripts/build_fork_pages.py`
- **THEN** файл `docs/fork-medium90-results.json` SHALL содержать по одной строке на
  конфигурацию с `{passed,total}` по каждой измеренной волне и 95% Wilson-интервалом

#### Scenario: Проверка актуальности данных

- **WHEN** выполняется `python3 scripts/build_fork_pages.py --check`
- **THEN** код возврата SHALL быть `0`, если JSON актуален, и `1` — если устарел

### Requirement: Страница-таблица результатов форка

Форк SHALL предоставлять статическую страницу `docs/fork-medium90.html`, которая
рендерит данные из `docs/fork-medium90-results.json` и содержит матрицу
**Harness × Wave** и per-config таблицу с 95% Wilson-интервалом.

#### Scenario: Отрисовка данных

- **WHEN** страница открывается в браузере
- **THEN** она SHALL отображать строки по конфигурациям и волнам, а неизмеренные волны
  помечать как `Unmeasured`, а не как `0/total`

### Requirement: Публикация через GitHub Pages

Форк SHALL публиковать каталог `docs/` через GitHub Pages, чтобы таблицы результатов
были видны на сайте, а не только в markdown.

#### Scenario: Доступность страницы

- **WHEN** GitHub Pages включён для ветки `main` и пути `/docs`
- **THEN** страница `fork-medium90.html` SHALL отдаваться по адресу
  `https://alex-kul777.github.io/harness-bench-fast/fork-medium90.html`

### Requirement: Реестр волн в авто-блоке

Генератор авто-блока `scripts/build_fork_results.py` SHALL регистрировать волны
новых задач как один umbrella-suite `Medium (392–471)` (long 20 + reflection 20 +
feasibility 40), чтобы прогоны этих волн попадали в `docs/fork-results.md`.

#### Scenario: Прогон новой волны

- **WHEN** в `results/` появляется JSON-прогон с именем волны long/reflect/feasibility
- **THEN** `python3 scripts/build_fork_results.py` SHALL включить его строку в авто-блок
  под сюжетом `Medium (392–471)`
