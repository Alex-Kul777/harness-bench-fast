# result-reporting (delta)

## MODIFIED Requirements

### Requirement: Данные страницы результатов форка

Форк SHALL генерировать `docs/fork-medium90-results.json` из JSON-прогонов
(`results/`) скриптом `scripts/build_fork_pages.py` по замороженной схеме (строки
конфигураций: `harness`, `model`, `profile`, `runs`, `suites` по волнам
long/reflect/feasibility, `usage`, `wilson`, `sources`). Свод по волне SHALL считаться
как UNION номеров задач, а не как сумма per-file итогов.

#### Scenario: Свод по волнам

- **WHEN** запускается `python3 scripts/build_fork_pages.py`
- **THEN** файл `docs/fork-medium90-results.json` SHALL содержать по одной строке на
  конфигурацию с `{passed,total}` по каждой измеренной волне и 95% Wilson-интервалом

#### Scenario: Перекрывающиеся артефакты волны не завышают покрытие

- **WHEN** по одной конфигурации и волне есть несколько артефактов с перекрывающимися
  номерами задач (напр. устаревший частичный прогон и догоняющий)
- **THEN** `total` волны SHALL равняться числу **уникальных** номеров задач, а `passed` —
  числу уникальных пройденных; перекрытие SHALL NOT суммироваться

#### Scenario: Нет разбираемых номеров задач

- **WHEN** ни один артефакт волны не даёт разбираемых номеров задач
- **THEN** скрипт SHALL сохранять прежнее поведение — суммировать `summary.passed` и
  `summary.total` этой волны

#### Scenario: Проверка актуальности данных

- **WHEN** выполняется `python3 scripts/build_fork_pages.py --check`
- **THEN** код возврата SHALL быть `0`, если JSON актуален, и `1` — если устарел
