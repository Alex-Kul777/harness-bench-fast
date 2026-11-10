# dedupe-fork-wave-tasks — tasks

## 1. Генератор (union-дедуп)

- [x] 1.1 `build_fork_pages.py`: читать per-task записи из `results` ИЛИ `tasks`; номер из `number`, иначе regex `task_(\d+)` (зеркало `build_fork_home._TASK_NUM_RE`)
- [x] 1.2 Per (config, wave): карта `номер → passed`; артефакты в возрастающем порядке имени файла (поздний перекрывает ранний)
- [x] 1.3 Итог волны = UNION: `total` = число различных номеров, `passed` = число `True`
- [x] 1.4 Fallback: волна без разбираемых номеров — сумма `summary` totals (старое поведение)
- [x] 1.5 `build_model(result_dirs=None)` — опциональный параметр каталогов, прокинут в `collect_paths`; существующие вызовы не сломаны

## 2. Спека / границы

- [x] 2.1 Дельта `result-reporting` (MODIFIED «Данные страницы результатов форка»: UNION-свод)
- [x] 2.2 `proposal.md`: Out of scope = агрегация usage (seconds/steps/tokens/cost_rub)
- [x] 2.3 `design.md`: документирован fallback на сумму при отсутствии номеров

## 3. Регрессионный тест

- [x] 3.1 `tests/test_fork_wave_task_union.py`: два перекрывающихся артефакта (2-task partial + 6-task catch-up) для одной config+wave → `total == 6`, `passed` ожидаемый
- [x] 3.2 Тест покрывает и источник `tasks` (OpenClaw), и источник `results` (Pi)

## 4. Verify / QA (для user-facing результата)

- [x] 4.1 `python3 -m pytest tests/test_fork_wave_task_union.py -q` — зелёный
- [x] 4.2 `python3 scripts/build_fork_pages.py` → long у off-конфига = 6 (не 8)
- [x] 4.3 `git add docs scripts tests openspec` + `python3 scripts/build_fork_results.py --check` == 0
- [x] 4.4 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0

## 5. Archive / land

- [x] 5.1 `openspec archive dedupe-fork-wave-tasks` (только после всех `[x]`)
