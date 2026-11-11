# Design: fix-hermes-runner-openspec

## ADR-inline

**Решение:** переиспользовать уже существующие общие хелперы форка вместо локальных
костылей Hermes-раннера: `harness_bench.artifact_metadata` (шапка),
`harness_bench.cost_resolver` (ставки/стоимость).

### Шапка метаданных

`_write_results` уже строит payload через `artifact_metadata(harness="hermes", ...)`
(коммит «record artifact metadata header»). Убираем зависимость от `thinking_off`:
уровень передаётся как `thinking=thinking_level` (`None` → `"default"` через
`normalize_thinking`). `harness_version` резолвится `resolve_harness_version(...,
detect=detect_harness_version)`, где autodetect парсит первую строку
`hermes --version` (напр. `Hermes Agent v0.23.1 (…) · stable · …`).

### Ставки модели и стоимость

`_get_model_rates(model)` = `resolve_model_rates(model)` (уже в коде). Заменяем
`compute_cost_rub(total_in, total_out, 0, 0, …)` на вызов с реальными cache-бакетами.
Никакого хардкода GLM-5.2 — регресс-тест это фиксирует.

### Cache/reasoning бакеты (parity с OpenClaw-раннером)

Hermes ведёт `cache_read_tokens`/`cache_write_tokens`/`reasoning_tokens` во внутреннем
учёте (`agent/usage_pricing.py`, `agent/turn_usage.py`), но verbose-строка
`Token usage: prompt=…, completion=…, total=…` их не несёт, а строка `💾 Cache: …`
подавляется `-Q` (`suppress_status_output`). Поэтому:

1. парсим явные cache-маркеры из stderr, если они есть (forward-compatible);
2. иначе в `_write_results` **один раз** выводим
   `cache_read = max(total - input - output, 0)`, `cache_write = 0`, записываем их
   и в per-task строку, и в `summary` — ровно как `run_openclaw_bench._write_results`.

`total_reasoning_tokens` — сумма per-task `agent_reasoning_tokens` (0, пока Hermes не
отдаёт поле; поле всё равно присутствует в `summary`).

### Уровень thinking

Штатный флаг `hermes chat --reasoning <level>` (0.22.1+) заменяет хак с
`hermes config set agent.reasoning_effort`. Так как `--reasoning` переопределяет
`agent.reasoning_effort` только на этот прогон, `--ignore-user-config` можно оставлять
включённым для всех задач, а восстанавливать конфиг после прогона больше не нужно.
Уровни: `none|minimal|low|medium|high|xhigh|max|ultra`; `--thinking-off` → `--thinking none`.

## Совместимость

- Memory-задачи (222–253) по-прежнему запускаются **без** `--ignore-rules`, чтобы
  AGENTS.md инжектился; provider остаётся `custom` с `OPENAI_BASE_URL`/`OPENAI_API_KEY`.
- `_write_status(..., model=…)` теперь принимает модель прогона (иначе — `DEFAULT_MODEL`),
  устраняя занижение ₽-ставок в статусе.

## Тесты

- `tests/test_runner_hermes_metadata.py`: шапка (`harness`/`thinking`/`task_set_version`/
  `model`/`harness_version`), cache/reasoning бакеты, вывод cache из total, стоимость
  по ставкам DeepSeek-V4.1-Flash (85.07 ₽ ≠ fallback GLM-5.2), список `THINKING_LEVELS`.
- RED→GREEN: тест падает на `origin/main` (cache не пишется, `thinking_off` хардкод)
  и зелёный после патча.
