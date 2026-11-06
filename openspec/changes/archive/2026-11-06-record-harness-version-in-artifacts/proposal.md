# record-harness-version-in-artifacts

## Why
На странице `docs/fork.html` колонка `Harness` не может показать версию харнеса
(`pi-mono 0.73.1`), потому что артефакты прогона её не содержат (только
`task_set_version` — версия набора задач). Upstream пишет версию в имени харнеса; чтобы
добиться паритета, раннер должен **записывать версию харнеса в артефакт** — тогда
колонка заполнится автоматически (плумбинг генератора уже готов, OpenSpec
`add-fork-profile-parity`).

## What Changes
- `harness_bench/runner.py`: новый сеттер `set_results_json_harness_version(version)` и
  поле верхнего уровня `harness_version` в `results_to_payload` (когда задано).
- `harness_bench/__main__.py`: флаг `--harness-version` для `run-cli` (+ fallback из env
  `HARNESS_BENCH_HARNESS_VERSION`); значение прокидывается в раннер на время прогона и
  сбрасывается в `finally` (как `set_results_json_command`).
- Генератор `scripts/build_fork_home.py` уже читает `harness_version` (менять не нужно).

## Impact
- `harness_bench/runner.py`, `harness_bench/__main__.py` (минимальные аддитивные правки —
  безопасны при мерже upstream). Данные/страницы не переписываются.
- Скрипты-обёртки прогонов должны передавать `--harness-version` (или env) — иначе поле
  не появится (см. design, follow-up).
