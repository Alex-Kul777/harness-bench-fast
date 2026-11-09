# Proposal: fix-test-env-provisioning

## Why

Сегодня `pytest tests/` в этом форке **не собирается**: collection прерывается
(`1962 tests collected, 3 errors`), потому что три тест-файла импортируют зависимости,
которых нет в окружении:

- `tests/test_chat_openai.py` → `langchain_openai` → `openai`
- `tests/test_rli_backend.py` → `harness_bench.rli_worker` → `deepagents`
- `tests/test_runner_policy.py` → `langgraph`

Ни в одной документированной команде установки (`uv pip install -e ".[gigachat,openrouter]"`)
не описан воспроизводимый способ поднять **тест/дев-окружение** так, чтобы весь
`tests/` собирался без import-ошибок. Из-за этого локальный прогон тестов и CI-подобная
проверка блокируются на сборе, а не на реальных падениях.

## What Changes

- Добавляется скрипт `scripts/setup_test_env.sh` — детерминированное, идемпотентное
  провижинирование тест/дев-окружения:
  - `uv venv .venv` (в изолированном venv внутри чекаута);
  - `uv pip install -e '.[openrouter]'` — базовые project-deps + extra `openrouter`
    (`langchain-openai==1.2.2`), который транзитивно тянет `openai`, `deepagents`,
    `langgraph`;
  - **fallback на pip**, если `uv` недоступен;
  - явная до-установка `langchain-openai==1.2.2 langgraph`, если после базового шага
    хотя бы один из `openai`/`deepagents`/`langgraph` всё ещё не импортируется;
  - финальный smoke-check импортов.
- Добавляется короткая заметка о провижинировании в `README.md` (раздел про установку),
  если её ещё нет.
- `pyproject.toml` — **без изменений**, если только не обнаружится реальный дефект
  манифеста (отсутствующий явный тест-деп). Предпочтение — не трогать манифест.
- Тест-файлы **не** правим: provisioning — канонический фикс, skip-guard'ы не добавляются.

## Capabilities

### New Capabilities
- `dev-environment`: новое требование — репозиторий SHALL предоставлять
  воспроизводимый способ провижинирования тест/дев-окружения (project deps + dev/test
  groups), чтобы `pytest tests/` собирался без import-ошибок.

### Modified Capabilities
- (нет)

## Impact

- Код/инфра: `scripts/setup_test_env.sh` (новый), `README.md` (короткая заметка),
  `openspec/changes/fix-test-env-provisioning/**` (артефакты).
- `pyproject.toml` — только если подтвердится реальная дыра в манифесте; по умолчанию
  не меняется (нет manifest churn).
- Тесты: правок в `tests/**` нет.
- **Out of scope:** добавление skip-guard'ов в 3 тест-файла, изменение pass/fail
  методологии, раннеров, `harness_bench/**`, git commit/push/merge. Провижинирование
  CI (`.github/workflows/*`) и общий CI-пайплайн — вне этого change.

## Workboard

- Card: не заводился (задача выдана субагенту через OpenSpec-change
  `fix-test-env-provisioning`; репозиторная норма — карточка Workboard для >5 мин).
