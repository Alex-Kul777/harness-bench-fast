# Design: move-runners-into-hbf

## Расположение файлов

Раннеры размещаются в корне HBF (не в `scripts/`), т.к.:
1. Скилл `harness-bench-fast` ссылается на них как `python3 run_pi_bench.py ...`
2. Существующие тесты используют `ROOT = Path(__file__).resolve().parents[1]`
   и загружают раннеры по имени из ROOT — это работает с `tests/` в HBF.

```
harness-bench-fast/
├── run_pi_bench.py          ← moved from workspace
├── run_openclaw_bench.py    ← moved from workspace
├── run_hermes_bench.py      ← moved from workspace
├── results/                 ← NEW: default store for run artifacts
├── tests/
│   ├── test_runner_pi_cleanup.py      ← moved from workspace
│   ├── test_runner_openclaw_version.py ← moved from workspace
│   └── test_runner_suite_selector.py   ← moved from workspace
└── harness_bench/           ← existing; раннеры импортируют отсюда
```

## Путь к harness_bench

Раннеры до переезда устанавливали:
```python
_DEFAULT_BENCH_DIR = str(Path(__file__).parent / "harness-bench-fast")
BENCH_DIR = Path(os.environ.get("BENCH_DIR", _DEFAULT_BENCH_DIR))
sys.path.insert(0, str(BENCH_DIR))
```

После переезда `harness_bench/` доступен прямо из `Path(__file__).parent`.
Новый код:
```python
BENCH_DIR = Path(os.environ.get("BENCH_DIR", str(Path(__file__).parent)))
sys.path.insert(0, str(BENCH_DIR))
```

Переменная `BENCH_DIR` сохраняется для совместимости с env override.

## results/ store

По умолчанию раннеры пишут `results/` относительно `BENCH_DIR`.
После переезда `BENCH_DIR` указывает на корень HBF → `results/` создаётся внутри HBF.

Если `BENCH_DIR` переопределён env-переменной — хранилище следует за ним
(старое поведение, обратная совместимость).

## Fork isolation

Раннеры — fork-specific additions. Они должны быть изолированы от upstream merges.
Добавляем заголовки `# FORK-OWNED: not in upstream ai-forever/harness-bench-fast`
к каждому перемещённому файлу.

## Deprecated pointers в workspace

В `openclaw-workspace/projects/benchmark-research/` оставляем
`RUNNERS_DEPRECATED.md` с объяснением и ссылкой на HBF.
Сами `.py` файлы НЕ удаляем (это follow-up).

## ADR

Решение соответствует ADR-0002: изменения поведения (путь запуска раннеров)
фиксируются через OpenSpec; engineering decisions (как именно) — в этом design.md.
