# fix-fork-steps-column — tasks

## 1. OpenSpec

- [x] 1.1 Proposal (`proposal.md`) с scope/out-of-scope + Workboard card `3f4b26cf`
- [x] 1.2 Delta `result-reporting`: «Заполнение колонки Steps»
- [x] 1.3 Delta `benchmark-runs`: MODIFIED «Единый формат результата» (+ сценарий OpenClaw)
- [x] 1.4 `design.md` (D1–D4, альтернативы, проверка, ветки)
- [x] 1.5 `openspec validate --all --strict` → 0

## 2. Fallback в генераторах (D1)

- [x] 2.1 Общий helper агрегации Steps (`steps_from_json`) в разделяемом модуле
- [x] 2.2 `build_fork_home.py`: приоритет агрегат → top-level → Σ `agent_steps`
- [x] 2.3 `build_fork_results.py`: тот же приоритет (авто-блок RU+EN)
- [x] 2.4 `—` только когда шагов нет нигде

## 3. Эмиссия агрегата в раннере (D2, репо openclaw-workspace)

- [x] 3.1 Ветка `fix/oc-runner-total-steps` от `main`
- [x] 3.2 `run_openclaw_bench.py::_write_results`: `summary.total_steps = Σ agent_steps`
- [x] 3.3 Тест/смоук: агрегат присутствует и равен сумме

## 4. Бэкфилл исторических артефактов (D3)

- [x] 4.1 Добавить `summary.total_steps` в закоммиченные `results/oc_shotlist_*.json`
- [x] 4.2 Проверить, что значения = Σ `tasks[].agent_steps` (247/120/328/148/237/244/224/244)

## 5. QA / верификация

- [x] 5.1 `tests/test_fork_steps_fallback.py` (агрегат / fallback / отсутствие)
- [x] 5.2 `build_fork_results.py --check`/`--lint`, `build_fork_home.py --check`, `build_fork_pages.py --check` → 0
- [x] 5.3 `tests/test_fork_bilingual.py` (паритет RU/EN) → ok
- [x] 5.4 Регенерация `docs/fork.html`(+`.en`), `docs/fork-results.md`(+`.en`) → колонка Steps заполнена
- [x] 5.5 Live-проверка `fork.html`/`fork.en.html` (после пуша — по команде владельца)

## 6. Финализация

- [x] 6.1 Коммит(ы) в ветке `fix/fork-run-steps` (main не трогаем)
- [x] 6.2 `openspec archive fix-fork-steps-column` после зелёного QA (по команде)
