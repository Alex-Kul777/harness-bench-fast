# result-reporting (delta)

## ADDED Requirements

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
