# result-reporting (delta)

## ADDED Requirements

### Requirement: Двуязычные страницы результатов

Страницы форка (`docs/fork.html`, `docs/fork-sample.html`, `docs/fork-run-<id>.html`,
`docs/fork-detail-<stem>.html`) SHALL публиковаться в русской локали (дефолт) и английском
зеркале (суффикс `.en.html`); при этом таблицы конфигов SHALL сохранять канонические
английские заголовки в обеих локалях.

#### Scenario: EN-зеркало страницы

- **WHEN** генерируется `docs/fork.html`
- **THEN** SHALL также генерироваться `docs/fork.en.html` с теми же данными и EN-подписями

#### Scenario: Канонические колонки в обеих локалях

- **WHEN** отображается таблица конфигов в любой локали
- **THEN** её заголовок SHALL содержать канонические английские колонки
  (`Harness`, `Profile`, `Model`, `Result`, `%`, `Time`, `Steps`, `Tokens (cost)`, `Version`)

#### Scenario: URL-hash сохраняется при смене локали

- **WHEN** активен таб и пользователь переключает локаль
- **THEN** URL-hash (например `#medium`) SHALL сохраняться на целевой странице

### Requirement: Двуязычный авто-блок результатов

Авто-блок в `docs/fork-results.md` SHALL генерироваться в RU-версии, а EN-зеркало
`docs/fork-results.en.md` SHALL содержать тот же набор строк с EN-подписями; канонические
английские колонки SHALL присутствовать в обоих файлах.

#### Scenario: Зеркало авто-блока

- **WHEN** выполняется `python3 scripts/build_fork_results.py`
- **THEN** SHALL обновляться авто-блок в `docs/fork-results.md` и его EN-зеркале
  `docs/fork-results.en.md`

#### Scenario: Паритет строк авто-блока

- **WHEN** сравниваются строки RU- и EN-авто-блока
- **THEN** множества строк данных SHALL совпадать (отличаются только подписи/заголовки групп)
