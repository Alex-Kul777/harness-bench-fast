# dev-environment Specification

## Purpose
Как тест/дев-окружение репозитория воспроизводимо провижинится (изолированный venv +
editable-пакет `-e .` + нужные extras), чтобы `pytest tests/` собирался без import-ошибок
(`openai` / `deepagents` / `langgraph`).

## Requirements

### Requirement: Воспроизводимое провижинирование тест/дев-окружения

Репозиторий SHALL предоставлять воспроизводимый способ провижинирования тест/дев-окружения
(project deps + dev/test groups) так, чтобы `pytest tests/` собирался без import-ошибок.
Провижинирование SHALL быть идемпотентным и изолированным (venv внутри чекаута) и SHALL
ставить editable-пакет `-e .` вместе с теми extras, что нужны тестам.

#### Scenario: Чистое провижинирование через скрипт

- **WHEN** пользователь запускает `scripts/setup_test_env.sh` в чистом чекауте с установленным `uv`
- **THEN** скрипт SHALL создать `.venv`, установить `-e '.[openrouter]'` и SHALL
  завершиться с ненулевым кодом, если `openai`, `deepagents` или `langgraph` не импортируются

#### Scenario: Fallback без uv

- **WHEN** `uv` недоступен в `PATH`
- **THEN** скрипт SHALL использовать `python -m venv` + `pip` для той же установки,
  SHALL NOT завершаться успехом при неимпортируемых тест-зависимостях

#### Scenario: До-установка недостающих тест-зависимостей

- **WHEN** после базового шага хотя бы один из `openai`, `deepagents`, `langgraph` не импортируется
- **THEN** скрипт SHALL до-установить недостающие зависимости (например
  `langchain-openai==1.2.2 langgraph`) и повторно проверить импорты

### Requirement: Коллекция тестов без import-ошибок

После провижинирования тест/дев-окружения `pytest tests/ --collect-only` SHALL собирать
весь набор тестов с **0 errors**. Тест-файлы SHALL NOT содержать skip-guard'ов, скрывающих
отсутствующие зависимости; отсутствующая зависимость SHALL лечиться провижинированием.

#### Scenario: Полная коллекция после провижинирования

- **WHEN** тест/дев-окружение провижинировано скриптом
- **THEN** `.venv/bin/python -m pytest tests/ --collect-only -q` SHALL завершаться с
  `0 errors`; наблюдаемое число собранных тестов зависит от состояния дерева и в этом
  чекауте равно `2025 tests collected`

#### Scenario: Ключевые зависимости импортируются

- **WHEN** провижинирование завершено
- **THEN** `.venv/bin/python -c "import openai, deepagents, langgraph"` SHALL
  выполняться без ошибок
