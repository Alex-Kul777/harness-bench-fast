# Design: fix-bench-token-accounting

## Root cause

### 1. Pi-раннер считает `usage` трижды (output ×3)

`pi --mode json` эмитит один и тот же объект `usage` assistant-ответа в нескольких
местах потока:

| событие | путь к `usage` | учитывался старым `_extract_usage` |
|---|---|---|
| `message_update` (дельты) | top-level | нет (пропускался) |
| `message_end` | `message.usage` | **да** |
| `turn_end` | `message.usage` (тот же объект) | **да** |
| `agent_end` | `messages[].usage` | **да** |

Рекурсивный обход всего потока поэтому умножал счёт на 3. Свидетельство — сырые
NDJSON (`/tmp/pi_bench_out_*.ndjson`, 242 файла, 171 из них gpt-5.5):

```
TRUE  in 7 075 512   out 536 600   cacheRead 24 609 152
RUNNER in 25 819 121 out 2 116 434     (ratio out 3.05, in 3.02)
```

Пример (task_392): один вызов `in=352 out=23 cacheRead=2528 totalTokens=2903`;
эти же значения встречаются в `message_end`, `turn_end` и `agent_end.messages[]`.

### 2. Pi-раннер теряет cache-бакеты (input занижен)

В `usage` есть `cacheRead`/`cacheWrite`, но раннер их не читал. Провайдер биллит
весь input (включая cached prefix) по входной ставке, поэтому потеря cache-бакета —
это недоучёт input. Инвариант Pi: `totalTokens = input + output + cacheRead + cacheWrite`
(проверено на сырых данных), значит `cacheRead = (total − input − output)`.

### 3. OpenClaw-раннер выводит cache вместо чтения явного поля

Конверт OpenClaw (`openclaw agent exec --json`, probe) содержит явные поля:

```json
"usage": {"input": 23491, "output": 163, "cacheRead": 12032, "cacheWrite": 0,
          "reasoningTokens": 17, "total": 35686, "cost": {"total": 1.635}}
```

Инвариант: `total = input + output + cacheRead + cacheWrite` (23491+163+12032=35686 ✔).
Старый раннер брал `usage.total` и пере-выводил cache как `total−input−output`
(почти верно, но терял `reasoningTokens` и не читал явные поля). `envelope.costUsd`
OpenClaw совпадает с ₽-оценкой и может служить источником истины; Pi `usage.cost.total`
всегда `0` — не пригоден.

## Billing model (проверено по выгрузке)

`cost = input_tokens*854 + output_tokens*5124` (±0,02%), где `input_tokens` — **весь**
input, включая cached prefix (т.е. cached input биллится по входной ставке). Для gpt-5.5
каталог публикует `cache_read = 85.4`, но фактический биллинг её не применяет — поэтому
в ₽-оценке gpt-5.5 cache-бакет тарифицируется по входной ставке (`854`).

## Reconciliation (провайдер vs наши, после правок)

Выгрузка разбита по billing-аккаунтам: волна **Pi** биллилась под `oait`, волна
**OpenClaw** — под `kap-openclaw` (контейнер Pi-раннера использует другой ключ).

| срез провайдера | calls | in | out | ₽ | наши (после правок) | Δ |
|---|---|---|---|---|---|---|
| `oait` (Pi) | 1553 | 31 804 295 | 568 044 | 30 063,70 | 29 908,05 | **−0,52%** |
| `kap-openclaw` (OC) | 1407 | 41 733 236 | 548 239 | 38 442,19 | 32 058,58 | −16,6% |
| `oait` + `kap-openclaw` | 2960 | 73 537 531 | 1 116 283 | 68 505,89 | 61 966,63 | −9,5% |

Итог: **Pi-волна сходится с провайдером в ±1%** (регресс-тест). OpenClaw-волна
недобирает ~17%, а суммарно — ~9,5% (непубликованные/повторные прогоны, которых нет
в артефактах). Точное «до копейки» совпадение с одним аккаунтом `kap-openclaw`
недостижимо: он содержит лишь часть наших прогонов (см. таблицу).

## Решение

- Pi: single-source учёт `usage` (только `message_end`/bare-`usage`; дедуп по
  `responseId`), запись cache-бакетов, цена cache в ₽-оценке.
- OpenClaw: чтение явных `usage.cacheRead`/`cacheWrite`; `total_reasoning_tokens`
  в summary; fallback — вывод из инварианта.
- Инвариант артефакта: `total_tokens = input + output + cacheRead + cacheWrite`.
- Бэкфилл 10 gpt-5.5 артефактов без перезапуска (данные восстанавливаются из
  сохранённых бакетов: Pi — деление ×3 + cache; OC — явный cache).
- Регресс-тест на обрезанном fixture-срезе выгрузки.

## Open items (не сошлось)

- OC-волна против `kap-openclaw`: −16,6%; суммарно −9,5% — аккаунт содержит не все
  прогоны (повторы/непубликованные запуски), восстановить их токены нельзя.
- Каталог `cache_read=85.4` для gpt-5.5 противоречит фактическому биллингу (input rate);
  здесь учтено в ₽-оценке точечно, общий политик-резолвер не менялся.
