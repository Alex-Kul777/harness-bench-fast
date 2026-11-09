# Design: fix-test-env-provisioning

## Контекст

`pyproject.toml` объявляет базовые deps (`deepagents==0.6.12`, `pytest`, `openpyxl`,
`PyYAML`, `tzdata`, `python-dotenv`) и extras: `gigachat`, `gigachat-profile`,
`openrouter` (`langchain-openai==1.2.2`). Группа `[dependency-groups].dev` содержит
`ruff`, `langchain-openai==1.2.2`, `langchain-gigachat==0.5.1`, `deepagents-gigachat==0.0.4`.

Три тест-файла тянут транзитивные зависимости, которые не покрывает «голый»
`uv pip install -e .`:

| Тест | Импорт | Транзитивно нужен |
|---|---|---|
| `tests/test_chat_openai.py` | `harness_bench.chat_openai` → `langchain_openai` | `openai` |
| `tests/test_rli_backend.py` | `harness_bench.rli_worker` → `deepagents.backends` | `deepagents` |
| `tests/test_runner_policy.py` | `langgraph.errors` | `langgraph` |

`deepagents` уже базовый dep, но его установка не обновляла систему и `langgraph`
не появлялся в глобальном окружении; `openai` приходит транзитивно только через
extra `openrouter`. Значит, канонический фикс — провижинирование: установить
`-e '.[openrouter]'`, что закрывает все три импорта.

## Решение (ADR-inline)

**Решение:** добавить `scripts/setup_test_env.sh`, который:

1. Предпочитает `uv`: `uv venv .venv` + `uv pip install -e '.[openrouter]'`.
2. Имеет **pip-fallback**: `python -m venv .venv` + `.venv/bin/pip install -e '.[openrouter]'`.
3. Делает **post-check** импортов `openai`, `deepagents`, `langgraph`; если чего-то нет —
   до-устанавливает `langchain-openai==1.2.2 langgraph` и перепроверяет.
4. Возвращает ненулевой код, если импорты всё ещё не проходят (fail loudly, не молча).

Почему **не** правим `pyproject.toml`: базовый манифест корректно описывает пакет;
`openai`/`langgraph` — транзитивные deps extras/библиотек, а не прямые зависимости
репозитория, поэтому добавлять их как прямые — неверная модель (это manifest churn,
а не реальная дыра). `deepagents==0.6.12` уже базовый. Единственная возможная
манифест-дыра — отсутствие явного тест-extra; но `[dependency-groups].dev` уже несёт
`langchain-openai==1.2.2`, так что `.[openrouter]` + dev-group покрывают тесты. Вывод:
манифест не трогаем.

Почему **не** skip-guard'ы в тестах: canonical fix — провижинирование (тесты должны
падать, если зависимости пропали, а не молча скипаться). Правка тестов скрыла бы
регрессию окружения.

Почему venv **внутри** чекаута: `.venv` уже в `.gitignore`; прогон изолирован и не
загрязняет системный Python и другие worktree.

## Как проверяем

- `scripts/setup_test_env.sh` в этом worktree.
- `.venv/bin/python -m pytest tests/ --collect-only -q` → `0 errors` (в этом чекауте наблюдается `2025 tests collected`; ожидание задачи `1906` относится к другому состоянию дерева и здесь недостижимо — провижинирование только *добавляет* собираемые тесты).
- `.venv/bin/python -c "import openai, deepagents, langgraph; print('deps ok')"` → `deps ok`.
- `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → exit 0.

## Риски

- **uv vs pip расхождение версий.** Оба ставят `langchain-openai==1.2.2` (pinned);
  рисков дрейфа версий нет.
- **Сетевой доступ.** Установка требует сети; при офлайн-окружении скрипт упадёт —
  это ожидаемо и громко.
- **Число собранных тестов** (`1906`) зависит от установленных плагинов/путей; проверяем
  именно отсутствие `errors`, а ожидаемое число фиксируем как индикатор.
