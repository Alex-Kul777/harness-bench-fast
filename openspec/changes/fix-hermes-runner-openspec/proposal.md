# Proposal: fix-hermes-runner-openspec

## Why

`run_hermes_bench.py` (харнесс Hermes) отстал от контракта OpenSpec-спеки
`benchmark-runs`, которому уже соответствуют Pi- и OpenClaw-раннеры:

1. **Неполная шапка метаданных.** Артефакт Hermes не гарантирует весь набор
   top-level полей (`harness`, `thinking`, `task_set_version`, `model`,
   `harness_version`) с корректным уровнем reasoning — `thinking_off` пишется как
   `"off"` хаком через `agent.reasoning_effort`, а не через штатный уровень.
2. **Нет cache/reasoning бакетов.** `summary` не содержит
   `total_cache_read_tokens` / `total_cache_write_tokens` / `total_reasoning_tokens`,
   а `compute_cost_rub` вызывается с cache = 0 — стоимость занижается.
3. **Нет уровня thinking.** Раннер умеет только `--thinking-off`, нет флага
   `--thinking <level>`, хотя Hermes 0.22.1+ поддерживает `hermes chat --reasoning`.
4. **Статус-файл хардкодит `DEFAULT_MODEL`** для ₽-ставок вместо модели прогона.

## What

Привести `run_hermes_bench.py` к контракту `benchmark-runs`:

- шапка метаданных через общий helper `harness_bench.artifact_metadata`;
- ставки модели через `harness_bench.cost_resolver.resolve_model_rates` +
  `compute_cost_rub` (никакого хардкода GLM-5.2), cache в стоимости;
- явные cache/reasoning бакеты в `summary` (вывод `max(total-input-output,0)` один раз,
  как в OpenClaw-раннере);
- флаг `--thinking <level>` → `hermes chat --reasoning <level>`, `--thinking-off`
  как алиас `--thinking none`; уровень пишется в `thinking` артефакта;
- `harness_version` через `resolve_harness_version` с autodetect `hermes --version`;
- regress-тест `tests/test_runner_hermes_metadata.py`;
- OpenSpec-дельта `benchmark-runs` с Hermes-сценариями.

## Capabilities

- `benchmark-runs` (MODIFIED + ADDED requirements)

## Impact

- `run_hermes_bench.py` — метаданные, стоимость, бакеты, флаг thinking.
- `tests/test_runner_hermes_metadata.py` — новый регресс-тест (RED→GREEN).
- Поведение memory-задач (222–253, без `--ignore-rules`) и `--provider custom`
  (OPENAI_BASE_URL/OPENAI_API_KEY) сохраняется без изменений.
- Публикуемые доки НЕ регенерируются (`build_fork_results.py --check` остаётся 0).

## Out of scope

- Изменение методологии pass/fail и верификаторов.
- Новые прогоны/волны и публикация результатов (доки форка не трогаются).
- Изменение Pi-/OpenClaw-раннеров (они уже соответствуют контракту).
- Коммит/push/merge в main.

## Links

- Workboard: `aebe1585`
- Issue: https://github.com/Alex-Kul777/openclaw-workspace/issues/445
