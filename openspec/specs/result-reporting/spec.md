# result-reporting

## Purpose

Как результаты форка представляются наружу: таблицы лидерборда, форк-слой
документации и автоматическая синхронизация таблиц из JSON-прогонов.

## Requirements

### Requirement: Канонические поля таблиц

Все таблицы результатов форка SHALL содержать колонки: `Harness`, `Profile`,
`Model`, `Result`, `%`, `Time`, `Steps`, `Tokens (cost)`.

#### Scenario: Добавление таблицы результатов

- **WHEN** таблица результатов добавляется в `FORK.md` или `docs/fork-results.md`
- **THEN** она SHALL содержать все канонические колонки

### Requirement: Автосинк авто-блока

Авто-блок в `docs/fork-results.md` SHALL генерироваться скриптом между маркерами
`<!-- FORK:RESULTS:BEGIN -->` и `<!-- FORK:RESULTS:END -->`.

#### Scenario: Проверка актуальности

- **WHEN** выполняется `python3 scripts/build_fork_results.py --check`
- **THEN** код возврата SHALL быть `0`, если блок актуален, и `1` — если устарел

### Requirement: Форк-слой не теряется при мерже upstream

Форк-слой в `README.md` SHALL быть обёрнут маркерами `<!-- FORK:BEGIN -->` …
`<!-- FORK:END -->`.

#### Scenario: Мерж upstream

- **WHEN** выполняется `git merge upstream/main`
- **THEN** баннер SHALL сохраняться, а при конфликте выбирается «keep ours»

### Requirement: Линт канонических колонок

Инструмент отчётности SHALL предоставлять режим `--lint`, проверяющий, что каждая
таблица результатов в `FORK.md` и `docs/fork-results.md` содержит колонки
`Harness`, `Profile`, `Model`, `Result`, `%`, `Time`, `Steps`, `Tokens (cost)`.

#### Scenario: Все таблицы корректны

- **WHEN** запускается `python3 scripts/build_fork_results.py --lint`
- **THEN** код возврата SHALL быть `0`, если во всех результатных таблицах есть канонические колонки

#### Scenario: Таблица без колонки

- **WHEN** какая-либо результатная таблица не содержит одну из канонических колонок
- **THEN** `--lint` SHALL вывести имя файла и список отсутствующих колонок и вернуть ненулевой код

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
**Harness × Wave** и per-config таблицу с 95% Wilson-интервалом. Per-config таблица
SHALL содержать канонические колонки форка `Profile`, `Time` и `Tokens (cost)`, а
ячейка `Model / harness` SHALL быть ссылкой на страницу детализации прогона
(`details_url`).

#### Scenario: Отрисовка данных

- **WHEN** страница открывается в браузере
- **THEN** она SHALL отображать строки по конфигурациям и волнам, а неизмеренные волны
  помечать как `Unmeasured`, а не как `0/total`

#### Scenario: Колонка Profile

- **WHEN** per-config таблица отрисовывается
- **THEN** она SHALL содержать колонку `Profile` (`—`, если профиль не задан)

#### Scenario: Колонка Tokens (cost) в рублях

- **WHEN** per-config таблица отрисовывается
- **THEN** колонка `Tokens (cost)` SHALL показывать токены и оценку стоимости в рублях (`₽`)
  из `row.usage.cost_rub`; при отсутствии стоимости SHALL показываться только токены

#### Scenario: Колонка Time

- **WHEN** per-config таблица отрисовывается
- **THEN** колонка `Time` SHALL показывать длительность прогона в минутах из
  `row.usage.seconds` (`—` при отсутствии)

#### Scenario: Ссылка на детализацию

- **WHEN** у строки задан `details_url`
- **THEN** ячейка `Model / harness` SHALL быть ссылкой на соответствующую страницу
  детализации прогона

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

### Requirement: Версионирование ассетов страницы

Ассеты опубликованной форк-страницы (`docs/fork-medium90.html`) SHALL подключаться с
query-версией (`…?v=<version>`), чтобы браузер не мог смешать устаревший закешированный
`fork-results.js` со свежей разметкой.

#### Scenario: Теги ассетов версионированы

- **WHEN** страница `docs/fork-medium90.html` публикуется
- **THEN** теги `<link>`/`<script>` SHALL содержать параметр `v`

#### Scenario: Обновление ассетов

- **WHEN** изменяется `docs/fork-results.js`
- **THEN** версия `v` в теге SHALL быть обновлена, чтобы клиенты получили новый файл

### Requirement: Страница детализации прогона

Генератор `scripts/build_fork_pages.py` SHALL создавать для каждой конфигурации
статическую страницу `docs/fork-run-<id>.html` с разбивкой по волнам, списком задач
(при наличии per-task записей) и источниками прогонов. Для упавших (и структурированных)
задач страница SHALL показывать читаемую причину и раскрывающийся вывод верификатора,
а не обрезанный сырой JSON.

#### Scenario: Генерация детализации

- **WHEN** запускается `python3 scripts/build_fork_pages.py`
- **THEN** по каждой строке SHALL создаваться `docs/fork-run-<id>.html`, а в JSON
  появляться поле `details_url`

#### Scenario: Источники экранированы

- **WHEN** страница детализации рендерит имена источников и сообщения задач
- **THEN** текст SHALL быть HTML-экранирован

#### Scenario: Оформленный вывод упавшей задачи

- **WHEN** задача имеет `passed=false` или структурированный `message`
- **THEN** колонка `Note` SHALL показывать короткую причину (ошибку, `reason` или ключевые
  поля верификатора), а ячейка SHALL содержать раскрывающийся `<details>` с
  pretty-printed JSON верификатора и текстом `error` (если он есть)

#### Scenario: Ошибка как причина

- **WHEN** у задачи непустой `error`
- **THEN** колонка `Note` SHALL показывать текст ошибки (например, `timed out after 3600s`)
