# add-result-table-lint — proposal

## Why

Требование: все таблицы результатов форка обязаны содержать канонические колонки
(`Harness`, `Profile`, `Model`, `Result`, `%`, `Time`, `Steps`, `Tokens (cost)`).
Сейчас это проверяется глазами и уже один раз было пропущено (таблица «Wave 19»).
Нужна дешёвая машинная проверка в CI.

## What Changes

- Новая опция `--lint` у `scripts/build_fork_results.py`: проверяет наличие
  канонических колонок во всех результатных таблицах `FORK.md` и `docs/fork-results.md`.
- Ненулевой код возврата и список отсутствующих колонок при нарушении.
- CI-джоба вызывает `--lint`.

Не **BREAKING**: поведение по умолчанию (генерация авто-блока) не меняется.

## Capabilities

- **New Capabilities**: — (нет)
- **Modified Capabilities**: `result-reporting` — добавляется требование о линте
  канонических колонок (delta-спека).

## Out of scope

- Автопочинка таблиц.
- Проверка служебных таблиц «Что | Где» (это не таблицы результатов).
- Изменение самого генератора авто-блока (он уже выдаёт канонические колонки).

## Impact

- `scripts/build_fork_results.py`, `.github/workflows/openspec-validate.yml`.
- Данные и upstream-слой не затрагиваются.

## Tracking

- Workboard: `72193dcc` (board project-a)
- Epic: #429
