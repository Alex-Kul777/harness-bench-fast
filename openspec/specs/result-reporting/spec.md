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
