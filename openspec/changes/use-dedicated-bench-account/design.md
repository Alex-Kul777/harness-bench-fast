# Design: use-dedicated-bench-account

## Контекст

Бенчмарк-прогоны оплачивались production-ключом `CLOUD_RU_API_KEY` (тот же, что
агентный бюджет). Ключ резолвился по-разному в каждом раннере, а OpenClaw-раннер
не управлял ключом вообще. Нужен единый выделенный аккаунт для всех моделей и
харнессов, с сохранением работоспособности при отсутствии нового ключа.

## Решение

### Единый резолвер ключа

`harness_bench/bench_credentials.py:resolve_bench_api_key(env=None, *, hermes_env_path=None, warn=True)`
возвращает `(key, source)` и пишет NOTE в stderr. Приоритет:

1. `CLOUD_RU_BENCH_API_KEY` — выделенный бенч-ключ (канонический).
2. `CLOUD_RU_KAP_HERMES` — legacy выделенный-ish ключ (env, затем `~/.hermes/.env`).
3. `CLOUD_RU_API_KEY` — production (крайний fallback).

Когда задан `CLOUD_RU_BENCH_API_KEY`, production-ключ не выбирается никогда.
`source` ∈ {`CLOUD_RU_BENCH_API_KEY`, `CLOUD_RU_KAP_HERMES`, `CLOUD_RU_API_KEY`,
`none`} и попадает в артефакт как `summary.bench_credential`.

### Раннеры

- **Pi**: модульная переменная `CLOUD_RU_API_KEY` теперь = результат резолвера;
  `BENCH_CREDENTIAL` пишется в `summary`.
- **Hermes**: то же; `OPENAI_API_KEY` для `--provider custom` берётся из
  резолвера (исправление production-first бага).
- **OpenClaw**: резолвер на уровне модуля; ключ экспортируется в дочернее
  окружение `openclaw agent exec` (`CLOUD_RU_API_KEY` + `CLOUD_RU_BENCH_API_KEY`).
  Провайдер-конфиг сохраняется, поэтому поведение при отсутствии env не ломается.

### Совместимость артефакта

Ключ добавляется только в `summary` (новое поле `bench_credential`) — контракт
top-level метаданных и `build_fork_results.py` не меняются; публикуемые доки не
регенерируются.

## Альтернативы

- **Отдельный env на каждый раннер** — дублирование логики и рассинхрон; отвергнуто.
- **Только Hermes-ключ как общий** — не выражает намерение «выделенный бенч-аккаунт»;
  оставлен как fallback для обратной совместимости.
- **Жёстко требовать `CLOUD_RU_BENCH_API_KEY`** — сломало бы существующие прогоны;
  поэтому мягкий fallback с NOTE.

## Риски

- OpenClaw может игнорировать env и брать ключ из secret store → ключ не
  переопределится, но и не сломается; покрыто NOTE/provenance в артефакте.
