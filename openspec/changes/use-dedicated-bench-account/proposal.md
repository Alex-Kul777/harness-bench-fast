# Proposal: use-dedicated-bench-account

## Why

Сейчас все бенчмарк-прогоны (модели × харнессы Pi / OpenClaw / Hermes) используют
production-ключ `CLOUD_RU_API_KEY` — тот же, что и агентный (боевой) бюджет. Из-за
этого бюджеты не разнести:

- `run_pi_bench.py` и `run_hermes_bench.py` берут `CLOUD_RU_API_KEY` первым, а
  `CLOUD_RU_KAP_HERMES` — лишь как fallback из `~/.hermes/.env`.
- `run_openclaw_bench.py` вообще полагается на конфиг OpenClaw (secret store id
  `CLOUD_RU_API_KEY`), не прокидывая ключ в окружение `openclaw agent exec`.
- Ни один артефакт не фиксирует, какой аккаунт оплатил прогон.

Владелец вводит **выделенный биллинг-аккаунт** для всех бенчмарков — канонический
env-ключ `CLOUD_RU_BENCH_API_KEY` (новый аналог production-ключа
`CLOUD_RU_API_KEY`; значение владелец заведёт в секрет/env).

## What

- Общий helper `harness_bench/bench_credentials.py:resolve_bench_api_key()` с
  приоритетом `CLOUD_RU_BENCH_API_KEY` → `CLOUD_RU_KAP_HERMES` (env, затем
  `~/.hermes/.env`) → production `CLOUD_RU_API_KEY`, плюс stderr-NOTE о выбранном
  источнике.
- Все три раннера резолвят ключ через helper и SHALL NOT использовать production
  `CLOUD_RU_API_KEY`, когда задан `CLOUD_RU_BENCH_API_KEY`.
- Hermes-раннер ставит `OPENAI_API_KEY` из резолвера (раньше брал
  `CLOUD_RU_API_KEY` первым — баг для разнесения бюджетов).
- OpenClaw-раннер прокидывает резолвнутый ключ в окружение `openclaw agent exec`
  (минимально, не ломая конфиг-провайдер).
- Каждый артефакт записывает источник ключа: `summary.bench_credential`.
- Регресс-тест `tests/test_bench_credentials.py` (RED→GREEN).
- OpenSpec-дельта `benchmark-runs` (ADDED requirement).

## Capabilities

- `benchmark-runs` (ADDED requirement)

## Impact

- `harness_bench/bench_credentials.py` — новый общий резолвер ключа.
- `run_pi_bench.py`, `run_openclaw_bench.py`, `run_hermes_bench.py` — резолвинг
  ключа через helper; `summary.bench_credential`; прокидывание ключа в окружение
  OpenClaw-вызова.
- `tests/test_bench_credentials.py` — новый регресс-тест.
- Контракт артефакта (`build_fork_results.py --check`) НЕ ломается: `summary`
  только дополняется ключом; публикуемые доки не регенерируются.

## Out of scope

- Ротация/хранение самого секрета `CLOUD_RU_BENCH_API_KEY` (владелец заводит его
  в секрет/env; репозиторий значение не хранит).
- Изменение методологии pass/fail, верификаторов и тарифов.
- Реальные прогоны/волны и публикация результатов.
- Изменение контракта top-level метаданных артефакта.

## Links

- Workboard: `3db2e107`
- Issue: https://github.com/Alex-Kul777/openclaw-workspace/issues/448
