## ADDED Requirements

### Requirement: Hermes-раннер: поддерживаемые флаги CLI 0.23.x

`run_hermes_bench` SHALL формировать вызов `hermes chat` только из флагов,
поддерживаемых Hermes 0.23.x, и SHALL NOT передавать `-v/--verbose` на
gateway/non-TTY пути (там он приводит к `exit=2: Unsupported gateway CLI options`).
Usage SHALL запрашиваться через `--format stream-json`. При `--provider custom`
раннер SHALL передавать endpoint и credential явно (`--base-url`/`--api-key`),
т.к. `--ignore-user-config` не подхватывает пользовательский провайдер.

#### Scenario: Команда без verbose

- **WHEN** `run_hermes_bench.build_chat_command(...)` собирает argv задачи
- **THEN** argv SHALL NOT содержать `-v`/`--verbose`, а SHALL содержать `--format stream-json`

#### Scenario: Провайдер custom получает endpoint и ключ

- **WHEN** раннер запускает задачу с `--provider custom`
- **THEN** argv SHALL содержать `--base-url` (Cloud.ru) и `--api-key` из
  `harness_bench.bench_credentials.resolve_bench_api_key()`

#### Scenario: Memory-задачи сохраняют AGENTS.md

- **WHEN** раннер запускает memory-задачу (222–253)
- **THEN** argv SHALL NOT содержать `--ignore-rules`, а для остальных задач SHALL содержать

### Requirement: Hermes-раннер: bare model id для custom-провайдера

`run_hermes_bench` SHALL передавать в `--model` идентификатор без ведущего префикса
провайдера при `--provider custom`: квалифицированный id Cloud.ru
(`<provider>/<org>/<model>`) SHALL приводиться к bare `<org>/<model>`.

#### Scenario: Cloud.ru префикс срезан

- **WHEN** модель задана как `custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash`,
  а провайдер — `custom`
- **THEN** argv SHALL содержать `--model deepseek-ai/DeepSeek-V4.1-Flash`, а SHALL NOT
  содержать префикс `custom-foundation-models-api-cloud-ru/`

#### Scenario: Bare id не портится

- **WHEN** модель уже задана в bare-форме (`deepseek-ai/DeepSeek-V4.1-Flash`)
- **THEN** значение `--model` SHALL остаться без изменений

### Requirement: Hermes-раннер: usage из stream-json

`run_hermes_bench` SHALL читать usage-статистику из JSONL stdout режима
`--format stream-json`: терминальное событие `result` SHALL давать
`agent_input_tokens`/`agent_output_tokens`/`agent_total_tokens`/
`agent_cache_read_tokens`/`agent_cache_write_tokens` и `session_id`. Раннер SHALL NOT
полагаться на regex по stderr verbose-вывода. При отсутствии события `result` токены
SHALL считаться нулевыми, а причина SHALL фиксироваться в поле `error` задачи.

#### Scenario: Токены взяты из result-события

- **WHEN** stdout содержит `{"type":"result","tokens":{"input":16311,"output":3,"total":16314,"cache_read":128,"cache_write":0}}`
- **THEN** per-task строка SHALL содержать эти значения, а `summary` SHALL агрегировать их
  в `total_input_tokens`/`total_output_tokens`/`total_tokens`/`total_cache_read_tokens`/`total_cache_write_tokens`

#### Scenario: Нет result-события

- **WHEN** в stdout нет события `result`
- **THEN** токены SHALL быть нулевыми, а поле `error` задачи SHALL описывать отсутствие
  result-конверта (SHALL NOT молча терять причину)
