# Proposal: fix-bench-token-accounting

## Why

Опубликованные ₽-результаты gpt-5.5 занижали фактический биллинг. Сверка с
провайдерской выгрузкой Cloud.ru (учётка `kap-openclaw`, модель `openai/gpt-5.5`)
дала **38 442,19 ₽** (`in = 41 733 236`, `out = 548 239`; проверено:
`cost = in*854 + out*5124`, ±0,02%), тогда как сумма наших 10 артефактов
(`results/*gpt55*{off,high}*20261110.json`) — **36 973,08 ₽**
(`in = 30 194 261`, `out = 2 127 703`): Δ = **−1 469 ₽ (−3,8%)**.

Диагностика (по сырому NDJSON и конверту OpenClaw) выявила две ошибки учёта:

1. **Pi-раннер задваивал (×3) токены.** `run_pi_bench._extract_usage` рекурсивно
   сканировал весь `--mode json` поток, поэтому один и тот же `usage` assistant-ответа
   попадал в счёт трижды: из `message_end`, из `turn_end` и из
   `agent_end.messages[]` (пропускались только `message_update`-дельты). Замер по
   сырым NDJSON: `runner/true ≈ 3,05` по output и `≈ 3,02` по input.
2. **Pi-раннер терял cache-бакеты.** В `usage` каждой записи есть
   `cacheRead`/`cacheWrite`, но раннер их не читал — а на длинных прогонах cached
   prefix это основной объём input. Провайдер биллит **весь** input (включая cached)
   по входной ставке, поэтому потеря cache-бакета = недоучёт input (~×1,38).

Плюс несоответствие в OpenClaw-раннере: он брал `usage.total` из конверта и
пере-выводил cache как `total − input − output`, игнорируя явные `cacheRead`/
`cacheWrite` конверта (и не писал `reasoningTokens` в summary).

## What Changes

1. `run_pi_bench.py`:
   - `_extract_usage` считает `usage` **ровно один раз** (только `message_end`
     либо одиночный объект с `usage`; `turn_end`/`agent_end`/`message_update` не
     считаются; дедуп по `responseId`);
   - читает `cacheRead`/`cacheWrite` и пишет
     `agent_cache_read_tokens`/`agent_cache_write_tokens` per-task;
   - `_write_results`/`_write_status`/`main` считают
     `summary.total_cache_read_tokens`/`total_cache_write_tokens` и включают их в
     `compute_cost_rub`.
2. `run_openclaw_bench.py`: `run_one_task` читает явные `usage.cacheRead`/
   `usage.cacheWrite`; `_write_results` использует их (иначе однократно выводит из
   инварианта `total = input + output + cacheRead + cacheWrite`), добавляет
   `summary.total_reasoning_tokens`.
3. `scripts/backfill_token_buckets.py` (новый): пересчитывает бакеты 10 gpt-5.5
   артефактов (Pi: снятие ×3 + cache-бакет; OC: явный cache-бакет) и ₽.
4. `tests/test_cost_gpt55_reconciliation.py` (новый) + fixture
   `tests/fixtures/gpt55_provider_slice.csv` (обрезанный срез выгрузки):
   регресс, что ₽-стоимость сходится с провайдером.

## Capabilities

### Modified Capabilities
- `benchmark-runs`: единый формат результата (cache/reasoning бакеты), учёт usage
  без задвоения, cache-бакеты Pi-раннера, провайдерская сверка ₽.
- `result-reporting`: колонка `Tokens (cost)` отражает ₽, включающую cache-бакет.

## Out of scope

- Смена тарифов моделей, кроме gpt-5.5 (см. design.md: цена cache-бакета).
- Перезапуск прогонов gpt-5.5 (данные восстанавливаются из уже сохранённых
  артефактов + сырого NDJSON).
- Сверка/бэкфилл остальных моделей за пределами 10 gpt-5.5 артефактов.
- Правка провайдерской выгрузки или аккаунтов `kap-openclaw`/`oait`.
- Причины расхождения с бюджетом аккаунта (второй billing-аккаунт, непубликованные
  прогоны) — фиксируются в design.md, но не «чинятся».

## Impact

- `run_pi_bench.py`, `run_openclaw_bench.py`, `scripts/backfill_token_buckets.py`
- `tests/test_runner_pi_cleanup.py` (семантика), `tests/test_cost_gpt55_reconciliation.py`,
  `tests/fixtures/gpt55_provider_slice.csv`
- `results/*gpt55*20261110.json` (10 артефактов: бакеты + `estimated_cost_rub`)
- `docs/fork-*` (перегенерация таблиц/страниц)

Ссылки: Workboard card `3bd7cfbb`, Issue
https://github.com/Alex-Kul777/openclaw-workspace/issues/444
