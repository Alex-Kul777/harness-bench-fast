# detect-oc-harness-crash — design

## Контекст

Крах `openclaw agent exec` (диагноз `docs/research/2026-11-17-openclaw-exec-crash-diagnosis.md`)
даёт: `returncode != 0`, непустой `stderr` с `MaxListenersExceededWarning` (и/или `403`,
и/или `Provider returned an incomplete or malformed tool call`), **0 usage**. Сейчас
`run_one_task` берёт `stderr_tail[-300:]` в `error` и пишет `passed=false` с 0 токенов —
неотличимо от честного провала.

## Решения

- **Q1 — что считаем крахом.** Дискриминаторы (любой): (a) `stderr` содержит один из
  маркеров инфры — `MaxListenersExceededWarning`, `EventEmitter memory leak`,
  `Use emitter.setMaxListeners`, `connect listeners added`; (b) `returncode != 0` **и**
  `usage` отсутствует/нулевой; (c) `error` содержит `Provider returned an incomplete or
  malformed tool call` при нулевом usage. Контентный `403` сам по себе — не краш (может
  быть ответом модели/guardrail), поэтому учитываем его только в паре с нулевым usage.
  Маркеры держим в одной константе `HARNESS_CRASH_MARKERS` (тестируемо).
- **Q2 — форма маркера.** Per-task: `harness_error: true`, `harness_error_kind` ∈
  {`listener_leak`, `provider_transport`, `unknown`}, `error` сохраняется как есть.
  Семантика `passed`: краш **не** делает задачу пройденной; но и **не** считается
  честным fail модели — прогон помечается несопоставимым (см. Q3).
- **Q3 — сопоставимость.** `summary.comparable = false`, если `harness_errors > 0`;
  `summary.harness_errors` (число) и `summary.harness_error_tasks` (список id). Это
  согласуется с существующей семантикой `comparable: false` (см. benchmark-runs,
  «Таймаут ниже флора не применяется молча»).
- **Q4 — ₽/токены.** Не выдумываем: `total_tokens=0`, `estimated_cost_rub=0` остаются
  фактом, но строка/прогон визуально помечены `invalid (harness error)` — не «бесплатный fail».
- **Q5 — обратная совместимость.** Поля аддитивны; старые артефакты без них читаются как
  `harness_errors = 0`, `comparable = true` (поведение по умолчанию).
- **Q6 — где чинить.** Детекция — в этом репо (раннер + reporting). Сам краш —
  продукт OpenClaw; в этом change-е НЕ трогаем.

## Альтернативы

- **Чинить `openclaw agent exec` здесь** — отвергнуто: код харнесса внешний
  (`~/.npm-global/lib/node_modules/openclaw`), не наш репозиторий.
- **Ретраить OC-задачу автоматически при крахе** — отложено: маскирует инфру и удорожает
  прогон; сначала достоверная метка, ретраи — отдельным решением.
- **Считать крах обычным fail** (текущее) — отвергнуто: искажает pass-rate и ₽.

## Открытые вопросы (для ревью)

- Отображать ли `invalid` на уровне строки таблицы (как `invalid`-волна) или только в
  детализации прогона? Предложение — строка получает пометку `invalid`, детализация
  показывает `harness_error_kind`.
- Нужен ли бэкфилл уже сохранённых 0-usage артефактов (393/398/431) — отдельный change.
