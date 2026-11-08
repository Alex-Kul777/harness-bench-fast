# Proposal: move-runners-into-hbf

## Контекст

Раннеры бенчмарков (`run_pi_bench.py`, `run_openclaw_bench.py`, `run_hermes_bench.py`)
и их тесты (`tests/test_runner_*.py`) исторически жили в `openclaw-workspace`
(репозиторий openclaw-config-backup) как соседи с папкой `harness-bench-fast/`.
Это создаёт неудобство: для запуска прогона нужна рабочая директория workspace, а не
только HBF. Раннеры хардкодили относительный путь `../harness-bench-fast` или
`./harness-bench-fast`, что ломается при смене корня.

## Цель

Раннеры и их тесты переезжают в HBF. Любой агент, клонировавший HBF, может сразу
запускать прогоны (`python3 run_pi_bench.py --pilot`) без требования к внешней
структуре папок.

## Решение (summary)

- Скопировать `run_pi_bench.py`, `run_openclaw_bench.py`, `run_hermes_bench.py`
  в корень HBF (или `scripts/`; выбираем корень для обратной совместимости с
  командами в скилле).
- Скопировать `tests/test_runner_*.py` в `tests/` HBF.
- Пофиксить импорты/пути: раннеры должны обнаруживать `harness_bench` по месту
  (`Path(__file__).parent`, т.к. `harness_bench/` лежит там же в HBF).
- Создать `results/` в HBF для хранения артефактов; задокументировать fallback.
- В openclaw-workspace оставить файлы-поинтеры с пометкой DEPRECATED; удаление —
  в отдельной задаче.
- Обновить скилл `harness-bench-fast` и `AGENTS.md` с новыми путями.

## Out of scope

- Удаление оригинальных файлов из openclaw-workspace (follow-up).
- Изменение бизнес-логики самих раннеров (добавление флагов, рефакторинг алгоритмов).
- Миграция исторических результатов из `openclaw-workspace/projects/benchmark-research/results/`.
- Настройка CI/CD на GitHub Actions.
- Изменение upstream-методологии (остаётся в README.md).
