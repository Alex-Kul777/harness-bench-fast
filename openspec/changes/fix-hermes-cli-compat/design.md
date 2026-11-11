# Design: fix-hermes-cli-compat

## ADR-inline

**Решение:** изолировать сборку argv и разбор usage в чистые функции
(`build_chat_command`, `_bare_model_id`, `_parse_stream_json`), чтобы CLI-совместимость
Hermes 0.23.x была юнит-тестируемой без запуска агента.

### Совместимость флагов

Hermes 0.23.1 на non-TTY/gateway отклоняет `-v` (`Unsupported gateway CLI options`).
Поэтому verbose отключён, а usage берётся из машиночитаемого `--format stream-json`
(protocol: `system/init` → `text`/`tool_use`/`tool_result` → терминальный `result`).
Событие `result` несёт `session_id`, `exit_code`, `text`, `tokens{input,output,total,cache_read,cache_write}`.

`--format stream-json` уже подразумевает `--quiet`, поэтому отдельный `-Q` не нужен.

### Провайдер custom

`--ignore-user-config` не подхватывает пользовательский провайдер, поэтому endpoint и
credential передаются явно: `--base-url $CLOUD_RU_BASE_URL` и
`--api-key $(resolve_bench_api_key())`. Дополнительно окружение всё ещё получает
`OPENAI_BASE_URL`/`OPENAI_API_KEY` (parity с Pi-/OpenClaw-раннерами).

### Bare model id

Идентификаторы Cloud.ru в форке квалифицированы провайдером
(`<provider>/<org>/<model>`), а Hermes `--provider custom` знает bare `<org>/<model>`.
`_bare_model_id` срезает известный префикс `custom-foundation-models-api-cloud-ru/`
(не любой первый `/`, т.к. сам model id содержит `deepseek-ai/`). Незнакомые префиксы
проходят без изменений.

### Разбор usage

`_parse_stream_json(stdout)` читает JSONL, считает `tool_use`-события
(`agent_steps` = число вызовов инструментов — parity с OpenClaw-раннером), берёт
токены и `session_id` из `result`. Если `result` нет — статистика пустая (→ нули в
`_write_results`), а `error` задачи получает `stream-json: no result event`.
`summary`/top-level метаданные уже строятся общим helper'ом и не меняются.

## Тесты

`tests/test_runner_hermes_stream_json.py`: фикстура — реальный `result`-JSONL
(input 16311 / output 3 / cache_read 128 / total 16314) + текст. Проверяет, что argv
не содержит `-v` и содержит `--format stream-json`/`--base-url`/`--api-key` с bare model,
а парсер берёт токены из `result` (и корректно деградирует без него).

RED→GREEN: на `origin/main` `build_chat_command`/`_parse_stream_json` отсутствуют и
команда содержит `-v` → тест падает; после патча — зелёный.
