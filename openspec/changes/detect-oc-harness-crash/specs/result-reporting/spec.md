## ADDED Requirements

### Requirement: Harness-крах отображается как invalid, а не fail

Форк-страницы результатов (`docs/fork.html`, `docs/fork-run-<id>.html`,
`docs/fork-detail-<stem>.html`) SHALL отображать задачу или прогон с `harness_error: true`
как `invalid (harness error)`, а SHALL NOT отображать его как обычный провал модели или как
сопоставимый `fail`.

#### Scenario: Строка прогона помечена invalid

- **WHEN** артефакт прогона содержит `summary.comparable = false` из-за `harness_errors > 0`
- **THEN** строка этого прогона SHALL показывать статус `invalid (harness error)`, а
  `Result`/`%` SHALL NOT трактоваться как честный провал модели

#### Scenario: Задача в детализации помечена

- **WHEN** на странице детализации прогона задача имеет `harness_error: true`
- **THEN** колонка `Note` SHALL показывать `harness error` (с `harness_error_kind`), а
  раскрывающийся блок SHALL содержать текст `error`

#### Scenario: Обычный провал модели не маскируется

- **WHEN** задача имеет `passed=false` без `harness_error`
- **THEN** она SHALL отображаться как обычный `fail` (сообщение/`reason`), а SHALL NOT
  помечаться как `invalid`

#### Scenario: Старые артефакты не ломаются

- **WHEN** артефакт не содержит полей `harness_errors`/`harness_error`
- **THEN** страницы SHALL рендериться как прежде (крахов нет)
