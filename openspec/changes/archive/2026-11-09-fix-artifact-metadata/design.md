# Design: fix-artifact-metadata

## ADR-inline

**Решение:** вынести метаданные-шапку артефакта в один helper
`harness_bench/artifact_metadata.py` и вызывать его из `_write_results()` каждого
из трёх раннеров. Источник истины версии набора задач — `harness_bench/versioning.py`
(`TASK_SET_REVISIONS`), отдельные константы не хардкодим.

## Контракт полей (top-level, имена заморожены)

| поле | тип | правило |
|---|---|---|
| `harness` | str | `"openclaw"` / `"pi"` / `"hermes"` (совпадает со набором `UPSTREAM_OURS`) |
| `harness_version` | str | пишется, когда версия известна; поле ОТСУТСТВУЕТ только если реально неизвестна |
| `thinking` | str | эффективный reasoning level; `"default"`, если не задан |
| `task_set_version` | str | корректен для волны (см. ниже), НЕ константа |
| `model` | str | точный id/версия модели прогона |

## Почему `task_set_version` вычисляется, а не берётся как текущий registry-версия

README фиксирует, что каждая волна принадлежит своей task-set revision:
v0.16.0 = Light 1–391, v0.17.0 добавляет long 392–411, v0.18.0 — reflect 412–431,
v0.19.0/v0.19.1 — wave 19 feasibility 432–471. Закоммиченные артефакты это
подтверждают (`*_full391_v016.json` → `0.16.0`, `*_full411_v017.json` → `0.17.0`).
Поэтому версия волны выводится из **максимального номера задачи** прогона.

### Алгоритм `task_set_version_for_tasks(task_ids)`

1. Извлечь номера задач (`versioning.task_number`); пусто → `TASK_SET_VERSION`.
2. `top = max(numbers)`.
3. Среди `TASK_SET_REVISIONS` взять ревизии с `total_tasks >= top`; выбрать
   **наименьший** `total_tasks` (самая «узкая» ревизия, покрывающая волну).
4. Среди ревизий с этим `total_tasks` вернуть **последнюю** (учитывает
   правки-протоколы без новых задач — 0.16.0, 0.19.1, 0.21.x).
5. `top` за пределами registry → `TASK_SET_VERSION` (текущая).

Результаты: 1–391 → `0.16.0`; 392–411 → `0.17.0`; 412–431 → `0.18.0`;
432–471 → `0.19.1`; 472–511 → `0.20.0`; 512–531 → `0.21.3`.

## `thinking`

`normalize_thinking(value)`: `None`/пусто → `"default"`, иначе `str(value).strip()`.
Раннеры передают свой эффективный уровень: OpenClaw `--thinking`;
Pi `--thinking` (level); Hermes `--thinking-off` → `"off"`, иначе `"default"`.

## `harness_version`

`resolve_harness_version(explicit, detect=...)`: `explicit` → env
`HARNESS_BENCH_HARNESS_VERSION` → best-effort `detect()` (guarded, не падает).
OpenClaw сохраняет существующий autodetect (`openclaw --version`). Pi/Hermes —
флаг `--harness-version` + env + best-effort; при неудаче поле опускается.

## Совместимость

`_write_results()` всех раннеров получает новые **опциональные** kwargs
(`thinking`, `harness_version`, `task_ids`), поэтому существующие тесты
(`tests/test_runner_openclaw_version.py`) и вызовы остаются валидными.
Порядок ключей/структура `summary` не меняются; `model` добавляется как новое поле.

## Тесты

- `task_set_version_for_tasks`: Light→0.16.0; long→0.17.0; reflect→0.18.0;
  feasibility→0.19.1; `!= "0.16.0"` для 392–471.
- `normalize_thinking`: `None`→`"default"`, `"high"`→`"high"`.
- По одному `_write_results`-тесту на раннер: поля записаны; волновой конфиг не `0.16.0`;
  reasoning по умолчанию `"default"`.
