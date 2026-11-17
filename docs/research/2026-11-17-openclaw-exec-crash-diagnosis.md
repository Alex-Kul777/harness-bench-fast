# Диагноз: краш `openclaw agent exec` на длинных задачах (0 usage)

**Дата:** 2026-11-17 · **Карточка:** `3cae8a52` · **Связано:** `8f99e6e8`, `28e03383` (OC 0-usage)
**Метод:** навык `diagnosing-bugs` (ask-matt → diagnosing-bugs). Продукт: `openclaw 2026.11.2 (b556fdf)`.

## Симптом
OC-нога на `task_403_binary_format_reverse` (DeepSeek-V4.1-Flash, `thinking=off`, `--timeout 7200`)
завершается **exit=1, 0 токенов**, задача не решается. Воспроизведено **2/2**.

## Red — наблюдённые ошибки (полный stderr)
Прогон #1 (1 шаг, 2967 с):
```
exit=1:  Use emitter.setMaxListeners() to increase limit
(node:2092032) MaxListenersExceededWarning: Possible EventEmitter memory leak detected.
11 connect listeners added to [Socket]. MaxListeners is 10.
Use emitter.setMaxListeners() to increase limit
Provider returned an incomplete or malformed tool call
```
Прогон #2 (14 шагов, 535 с):
```
exit=1: rsExceededWarning: Possible EventEmitter memory leak detected. 11 connect listeners added to [Socket].
MaxListeners is 10. Use emitter.setMaxListeners() to increase limit
[state/agent-db] agent database clean-close receipt: written
403 Input text May contain sensitive information, please try again.
```

## Гипотеза (falsifiable)
Провайдер Cloud.ru изредка отдаёт **403 guardrail** (`Input text May contain sensitive information`)
и/или **неполный tool-call**. OpenClaw корректно распознаёт второй случай как «пред-диспатч rejection»
и **ретраит ход** — см. `dist/message-patterns-*.mjs`:
`PRE_DISPATCH_TOOL_CALL_REJECTION_MESSAGES ⊇ "Provider returned an incomplete or malformed tool call"`,
и `dist/sdk-*.mjs` (`incomplete-turn-recovery`, `MALFORMED_TOOL_CALL_ARGUMENTS_ERROR_CODE`).
Ретраи идут поверх одного keep-alive `[Socket]` (undici) → на каждый `connect` добавляется листенер →
>10 → `MaxListenersExceededWarning`. Раннер видит непустой stderr + `returncode≠0` → `exit=1` → **0 usage**.

## Опровергнуто частично
Одиночные API-запросы к Cloud.ru с подозрительным контентом (base64-блоб, бинарные байты, PII-карта) →
**200**, не 403. Значит 403 **не** от простого контента; триггер специфичен для контента задачи
(вероятно — конкретный tool-result, возвращаемый модели). Требует отдельной инструментовки.

## Минимальный репро
Детерминированный (уровень харнесса):
```bash
python3 run_openclaw_bench.py \
  --tasks task_403_binary_format_reverse --thinking off \
  --model custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash \
  --timeout 7200
# → exit=1, 0 tokens, MaxListenersExceededWarning на [Socket]
```
См. `scripts/repro_oc_longtask_crash.sh`.

## Куда смотреть (fix)
1. Сокет/листенеры при ретраях провайдера: не копить `connect`-листенеры на переиспользуемом `[Socket]`
   (или `setMaxListeners`), и не завершать процесс `exit=1` из-за warning.
2. Пред-диспатч rejection: после N ретраев отдавать внятную ошибку, а не накручивать листенеры.
3. Cloud.ru guardrail: снять/ослабить фильтр для bench-контента (обратная сторона: риск ложных 403).

## Примечание о границах
Баг в `openclaw agent exec` (продукт OpenClaw), **вне** репозитория `harness-bench-fast`;
issues в bench-репо отключены → трекаем карточкой + этого дока.

## 9. КОРРЕКЦИЯ (2026-11-17, полный stderr) — лик = шум, причина другая
Инструментированный ручной прогон `task_403` под чистым bench-конфигом, **полный stderr**
(`/tmp/oc_instr.stderr`, `--timeout 1200`) дал точную цепочку. Прежняя гипотеза
(«plugin/MCP → лик листенеров → краш») **опровергнута**.

Факты из stderr:
1. `agent exec` **читает ambient config** (`[secrets] … resolved command secrets locally`)
   — но на чистом конфиге всё равно падает ⇒ дело не в plugins/MCP.
2. Идут длинные ходы: ~54 assistant-turn; тело запроса растёт **142 KB → 2.2 MB**,
   `promptTokens` до ~443K; `[prompt-cache] cache read dropped …` много раз.
3. `[provider-transport-fetch] … causeName=SocketError causeCode=UND_ERR_SOCKET
   message=fetch failed` (request 23, 44) → `transient same-model retry 1/8`.
4. `output-limit continuation 1/1` (вывод упёрся в лимит → возможная обрезка tool-call).
5. Финал: `Provider returned an incomplete or malformed tool call` →
   `Assistant attempt failed` → `embedded run … isError=true` → `kind: incomplete_turn`.
6. `[state/agent-db] clean-close` → **пачка 8× `MaxListenersExceededWarning`** на `[Socket]`
   уже **при завершении процесса**, затем `exit=1`.
7. Envelope: `usageReport.state = "unavailable"` → раннер пишет **0 токенов**.

**Вывод:** `MaxListenersExceededWarning` — **teardown-шум** от множества сокетов/ретраев,
а **не** причина. Настоящий сбой — провайдер/модель возвращает **incomplete/malformed
tool call** (kind `incomplete_turn`) на очень длинном, раздутом контексте, плюс
transient `UND_ERR_SOCKET`; после исчерпания ретраев ход падает, usage = unavailable → 0.

**Что мы (вызов) сделали хуже:** чистый bench-конфиг **выбросил**
`agents.defaults.contextPruning` + `agents.defaults.compaction` (в боевом они есть:
compaction `maxActiveTranscriptBytes=10mb`, `keepRecentTokens=30000`). Возвращены в
`bench/openclaw.bench.json`.

**Кандидаты «починить вызов»:**
- вернуть pruning/compaction (сделано);
- проверить `maxTokens: 8192` провайдер-модели как причину обрезки tool-call;
- ретраить задачу при `incomplete_turn` (`--rerun-on-fail`), т.к. сбой может быть транзиентным;
- (к лику отношения не имеет; `NODE_OPTIONS=defaultMaxListeners` не нужен — это шум).

## 10. Тест-2 (bench-конфиг + pruning/compaction) — 2026-11-17
Прогон `task_403` под `bench/openclaw.bench.json` **с возвращёнными**
`contextPruning`/`compaction`:
- **FAIL**, но **1056.5 s** (было 265 s), 38 шагов;
- **usage ДОСТУПЕН**: 8 727 827 токенов (1 427 819 input / 56 744 output);
- та же терминальная ошибка: `Provider returned an incomplete or malformed tool call`
  (`kind: incomplete_turn`) + `MaxListenersExceededWarning` ×N при teardown.

**Вывод:** pruning/compaction улучшают ход (в 4× длиннее, usage фиксируется), но **не**
устраняют malformed tool call. Т.е. корневой сбой — на границе **провайдер/модель**
(недетерминированный мусорный tool-call), а не в настройках нашего вызова. Модель
`maxTokens=16384`; перед падением был `output-limit continuation 1/1` → вероятная обрезка
tool-call.

**Рычаги на нашей стороне (без правки продукта):**
1. **Ретрай задачи** при `incomplete_turn`/`usage unavailable` в раннере (N попыток) — дёшево.
2. **Поднять `maxTokens`** модели в bench-конфиге (16384 → выше) — меньше обрезки.
3. Эскалация к Cloud.ru по качеству tool-call у `DeepSeek-V4.1-Flash`.

## 11. Тест-3 (реализованный вариант: pinned config + maxTokens 32768 + retry 1) — 2026-11-17
**PASS 1/1** — `task_403_binary_format_reverse`, 4382.2 s, «скрытые файлы: верно 40/40».
Лог: `[1/1] … starting...` → `retryable infra crash (incomplete_turn) — attempt 2/2`
→ `[✅ PASS]`. **Попытка 1 упала с `incomplete_turn`, попытка 2 прошла.**

⇒ **Рычаг B (ретрай) подтверждён в бою**: без него прогон снова был бы записан как
ложный провал модели, хотя агент решает задачу. Изоляция + maxTokens + retry —
работающая комбинация.

### ⚠️ Новый нюанс: 0 токенов при `usage_available=True`
Артефакт тест-3: `agent_usage_available: True`, но `agent_*_tokens = 0`, `agent_turns=38`,
`agent_steps=1`. Контрольный смоук той же командой (`--config …`) показал **нормальную**
форму: `{"usageReport":{"state":"available"},"input":10421,"output":161,"total":30934,…}`.
Похоже, финальный конверт успешного прогона в retry/continuation-пути отдаёт
`usageReport.state=unavailable` (или пустые бакеты), и `_reported_usage` считает непустой
dict доступным → 0. Это **token-accounting**, отдельная тема (change
`fix-bench-token-accounting`), НЕ этот PR. Зафиксировать как follow-up.
