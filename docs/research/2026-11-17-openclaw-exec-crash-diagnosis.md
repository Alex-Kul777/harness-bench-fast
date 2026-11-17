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
