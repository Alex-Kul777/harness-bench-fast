# add-dsh-harness — design

## Контекст

`dsh` — официальный launcher DeepSeek Harness: он «загружает» профиль (упорядоченный
набор plugin-bundle patch-слоёв). Launcher-флаги (`--profile`, `--patch`) идут ДО
аргументов приложения; сам headless-апп (`--json`, `--permission-mode`, задача) —
после. Провайдер-роут (Cloud.ru) инжектится временным patch-файлом, а не аргументами
CLI. Формат вывода — NDJSON; usage приходит на каждый шаг в `status.step_end.usage`.

## Решения

- **Q1 — транспорт:** профиль `headless` + `--json` (NDJSON), как проверено вживую;
  headless-апп сам пишет финальный ответ в `final.text`.
- **Q2 — провайдер через патч:** на каждый прогон генерируется temp-`patch.yml`
  (`build_provider_patch`), который задаёт роут `cloudru` (`baseURL`, `api`,
  `apiKeyEnv: DSH_BENCH_API_KEY`, `reasoning`) и дефолтную модель. Секрет НИКОГДА не
  попадает ни в argv, ни в патч — только имя env-переменной.
- **Q3 — изоляция:** `DSH_HOME` указывает на отдельный каталог (`/tmp/dsh-home-bench`),
  чтобы пользовательские плагины/креды не протекали в прогон.
- **Q4 — bare model id:** Cloud.ru-иды несут провайдер-префикс
  (`custom-foundation-models-api-cloud-ru/...`); патч ожидает bare-ид
  (`deepseek-ai/DeepSeek-V4.1-Flash`), префикс срезается (`_bare_model_id`).
- **Q5 — usage из `status.step_end`:** каждый `step_end.usage` — это дельта шага
  (`inputTokens`/`outputTokens`/`totalTokens`/`cacheReadTokens`/`cacheWriteTokens`);
  сумма по всем `step_end` даёт баки прогона, `steps` = число `step_end`,
  `tool_calls` = число `tool_call`.
- **Q6 — `passed`:** exit code == 0 И `final.reason.kind == 'completed'` И верификатор
  задачи прошёл (как в прочих раннерах, плюс явная проверка reason).
- **Q7 — thinking:** `--thinking <level>` маппится в `reasoning` провайдер-роута
  (`none`/`off` → `off`), значение пишется top-level в артефакт.
- **Q8 — стоимость:** через `resolve_model_rates`/`compute_cost_rub` (как Hermes); при
  отсутствии ставки — fallback и пометка `rates_available: false` (не молча).

## Альтернативы

- Передавать провайдер флагами CLI вместо патча — отвергнуто: `dsh` не принимает
  endpoint/креды аргументами приложения, только через patch-слои профиля.
- Парсить stderr-диагностику для usage — отвергнуто: `--json` даёт структурированный
  NDJSON (`status.step_end.usage`), stderr остаётся `dsh:`-диагностикой.
- Свой launcher-профиль вместо `headless` — отвергнуто: профиль `headless` — штатный
  one-shot режим, минимальный и стабильный.

## Границы и риски

- Формат NDJSON — контракт `dsh 0.2.2-rc.1`; при мажорном апгрейде парсер покрыт
  регресс-тестом.
- `ultra` входит в `--thinking` по требованию задачи; если провайдер-роут не примет
  уровень, dsh отвергнет патч (fail-closed, не молча).
- Раннер не публикует артефакт (публикация — отдельный оркестратор); `--json-output`
  пишется атомарно, checkpoint/`--fresh`/`--rerun-on-fail` — как у Hermes.
