# Proposal: fix-hermes-cli-compat

## Why

Hermes обновился до **0.23.1**, и прогон Hermes shot-list дал **0/52**. Воспроизведены
три root cause в `run_hermes_bench.py::run_one_task`:

1. **`-v` больше не поддерживается** `hermes chat` на gateway/non-TTY: процесс падает
   с `exit=2: Unsupported gateway CLI options: --verbose` → все задачи FAIL.
2. **`--ignore-user-config` без явных провайдер-флагов** → turn не завершается
   (`Worker execution is unknown`), т.к. провайдер `custom` остаётся без endpoint/credential.
3. **model id с префиксом провайдера** `custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash`
   → `HTTP 404`: Hermes `--provider custom` ожидает **bare** id `deepseek-ai/DeepSeek-V4.1-Flash`.

Проверенная рабочая команда завершает turn и отдаёт токены:
`hermes chat -q … --model <bare> --provider custom --base-url … --api-key … --ignore-user-config --yolo --format stream-json --max-turns 120 --source tool --reasoning <level>`,
где `--format stream-json` печатает JSONL с терминальным событием `{"type":"result",…,"tokens":{…}}`.

## What

Привести раннер Hermes к CLI 0.23.x:

- **Команда**: убрать `-v`; добавить `--format stream-json`; при `--provider custom`
  передавать `--base-url` (Cloud.ru) и `--api-key` (из `harness_bench.bench_credentials.resolve_bench_api_key()`);
  оставить `--ignore-user-config`, `--yolo`, `--max-turns`, `--source tool`, `--reasoning <level>`;
  `--ignore-rules` — по-прежнему для всех задач, кроме memory-задач 222–253.
- **Model id**: для `--provider custom` срезать ведущий префикс провайдера
  (`custom-foundation-models-api-cloud-ru/`) перед передачей в `--model`.
- **Токены**: вместо regex по stderr `-v` разбирать stdout как JSONL, найти `result`-событие
  → `tokens.input/output/cache_read/cache_write/total` и `session_id`. `agent_*`-поля и
  `summary` (вкл. `total_cache_read_tokens`/`total_cache_write_tokens`, `total_reasoning_tokens`,
  `bench_credential`) сохранить; top-level `artifact_metadata` не трогать. Fallback: нет
  `result` → нули, но ошибка фиксируется в `error`.
- **Регресс-тест** `tests/test_runner_hermes_stream_json.py`.
- **OpenSpec-дельта** `benchmark-runs`.

## Capabilities

- `benchmark-runs` (ADDED requirements)

## Impact

- `run_hermes_bench.py` — сборка команды (`build_chat_command`), bare model id (`_bare_model_id`),
  разбор stream-json (`_parse_stream_json`).
- `tests/test_runner_hermes_stream_json.py` — новый регресс-тест (RED→GREEN).
- Поведение memory-задач (222–253, без `--ignore-rules`) и `--provider custom` с
  `OPENAI_BASE_URL`/`OPENAI_API_KEY` в окружении сохраняется.
- Публикуемые доки НЕ регенерируются (`build_fork_results.py --check` остаётся 0).

## Out of scope

- Изменение методологии pass/fail и верификаторов.
- Новые прогоны/волны и публикация результатов.
- Изменение Pi-/OpenClaw-раннеров.
- Обновление Hermes или его конфигурации.
- Коммит/push/merge в main.

## Links

- Repo: `projects/benchmark-research/harness-bench-fast`
- Диагноз воспроизведён на Hermes Agent v0.23.1.
