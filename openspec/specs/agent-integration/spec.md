# agent-integration

## Purpose

Как агент OpenClaw работает с репозиторием: скилл репозитория и spec-driven
жизненный цикл OpenSpec (explore → propose → apply → verify → archive).

## Requirements

### Requirement: OpenSpec workflow

Репозиторий SHALL предоставлять агентский workflow OpenSpec, покрывающий стадии
explore → propose → apply → verify → archive.

#### Scenario: Изменение поведения идёт через change

- **WHEN** агент планирует изменение поведения системы
- **THEN** он SHALL сначала создать `openspec/changes/<id>/` (proposal, дельта спек,
  design, tasks) и получить ревью до реализации

### Requirement: Валидация спек в CI

CI SHALL запускать `openspec validate --all --strict` на pull request.

#### Scenario: Некорректная спека

- **WHEN** change содержит requirement без ключевого слова `SHALL`
- **THEN** валидация SHALL падать, и PR SHALL не мержиться
