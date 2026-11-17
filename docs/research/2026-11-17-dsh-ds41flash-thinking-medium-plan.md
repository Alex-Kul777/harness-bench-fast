# План: DeepSeek Harness × DeepSeek-V4.1-Flash на `thinking: medium`

Статус: **research / план** (read-only). Код не меняется — раннер уже поддерживает уровень.
Дата: 2026-11-17. Автор: project-a-agent.

> ## ❌ ИТОГ ПРОВЕРКИ (2026-11-17): через dsh **невозможно**
> Прогон `--shot-list --thinking medium` падает **52/52** мгновенно (steps=1, 0 токенов).
> Прямая проба dsh дала:
> ```
> UNSUPPORTED_REASONING_EFFORT: pi-ai provider "cloudru" model
> "deepseek-ai/DeepSeek-V4.1-Flash" does not support reasoning effort "medium"
> ```
> Пробинг всех schema-валидных уровней для этой модели через dsh/pi-ai:
>
> | уровень | off | minimal | low | medium | high | xhigh | max |
> |---|---|---|---|---|---|---|---|
> | dsh/pi-ai | ✅ OK | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
>
> ⇒ **только `off`** (тот самый профиль 51/52). Ограничение — в каталоге
> возможностей pi-ai (клиентская сторона dsh), **а не** в Cloud.ru API
> (сырой API принимает `medium`; см. OpenClaw-путь). **Вывод: план ниже неосуществим
> для dsh в текущем виде** — см. §10 «Что реально можно».

## 1. Цель

Прогнать тот же бенчмарк, что дал эталонную карточку ниже, но с уровнем
**`thinking: medium`** вместо `off`, чтобы получить сравнимую строку
«dsh × DeepSeek-V4.1-Flash × medium».

Эталон (уже есть):

| Поле | Значение |
|---|---|
| Harness | DeepSeek Harness (`dsh`) `0.2.2-rc.1` |
| Модель | `deepseek-ai/DeepSeek-V4.1-Flash` (cloud.ru) |
| Профиль | `thinking: off` (2026-11-11) |
| Набор | **shot-list, 52 задачи** |
| Результат | **51/52 (98.1 %)** |
| Время | 19.1 m (1143 s) |
| Шаги | 266 (tool-calls 304) |
| Токены | 1 975 401 · ~43 ₽ |
| Артефакт | `results/dsh_shotlist_ds41flash_off_20261111.json` |
| timeout / mode | 660 s · `workspace-write` |

## 2. Ключевой вывод (главное)

**Ничего писать не нужно.** `run_dsh_bench.py` уже принимает `--thinking medium`:
`_patch_reasoning_level("medium")` → `"medium"`, и это уходит в YAML-patch как
`reasoning: medium` для провайдера `cloudru`. Уровень `medium` входит в принимаемый
Cloud.ru набор (`none, minimal, low, medium, high, xhigh, max, ultra`) — т.е. валиден.

`THINKING_LEVELS = ("none","off","minimal","low","medium","high","max","ultra")` —
`medium` поддержан раннером и валидатором.

⇒ Это **операционный** прогон, а не разработка. План ниже — как его корректно сделать.

## 3. Как прогнать (рекомендованный вариант)

Тот же набор, что и эталон (**shot-list, 52 задачи**) — чтобы строки сравнивались «в лоб»:

```bash
cd <HBF>   # ~/.openclaw/workspace/projects/benchmark-research/harness-bench-fast
python3 run_dsh_bench.py --shot-list \
  --model deepseek-ai/DeepSeek-V4.1-Flash \
  --thinking medium \
  --concurrency 2 \
  --timeout 1800 \
  --permission-mode workspace-write \
  --json-output results/dsh_shotlist_ds41flash_medium_20261117.json \
  --status-file /tmp/dsh_shotlist_medium_status.json
```

Ключ (dedicated bench-credential) раннер резолвит сам
(`CLOUD_RU_BENCH_API_KEY → CLOUD_RU_KAP_HERMES → CLOUD_RU_API_KEY`); в командной строке
секрет не появляется (patch ссылается только на имя env-переменной `DSH_BENCH_API_KEY`).

Альтернатива — существующий скрипт, но **другой набор** (Medium-66, не сравнимо с 51/52):

```bash
LEVELS=medium bash scripts/run_dsh_medium66_ds41flash.sh
# = long(6) + reflect(20) + feasibility(40) с флорами таймаутов 7200/1800/3600
```

## 4. Сравнимость

Строка будет напрямую сопоставима с `off` (51/52), т.к. совпадают:
раннер, набор (shot-list), модель+провайдер, версия dsh, permission-mode, концуррентность.
Единственное отличие — `reasoning: medium`.

## 5. Ожидания (оценки, не гарантии)

- **Токены/₽:** reasoning-токены тарифицируются (output-категория) ⇒ суммарные токены и
  стоимость вырастут. Грубая вилка: `off`=43 ₽ → `medium` ≈ **×1.5–3 → ~60–130 ₽**
  (оценка; точных данных по medium для этой модели нет).
- **Время:** reasoning добавляет латентность перед ответом; вероятно **>19 m**.
- **Pass-rate:** ожидаемо ≥ `off` (medium может помочь на hard long-задачах, но может и
  не изменить — модель та же). Не гарантируется рост.

## 6. Риски и нюансы

1. **Таймаут.** Эталон шёл с `timeout=660`. При `medium` long-задачи (392/398/403 и др.)
   могут не уложиться. Рекомендация: `--timeout 1800`, а long-волну при необходимости —
   отдельным прогоном с флором 7200 (как в `medium66`).
2. **Guardrail Cloud.ru.** Ранее на контенте long-задач наблюдался
   `403 Input text May contain sensitive information` (в OpenClaw-пути). dsh-путь может
   тоже задеть; не фатально, но фиксировать в артефакте/логе.
3. **Профиль на странице fork-results.** Карточка помечает «Профиль: thinking: off
   (2026-11-11)». Для medium появится **новый профиль**; проверить, что
   `scripts/build_fork_results.py` корректно подпишет уровень (берёт из имени файла,
   `THINKING_OFF_SUFFIX`), и что HTML-страница парсит файл с `_medium_`.
4. **Стоимость ×K.** Если делать K=3 — стоимость ×3.

## 7. Открытые вопросы (решить до запуска)

- **Набор:** shot-list 52 (сравнимо с карточкой) **или** Medium-66 (шире покрытие, иная
  база)? → рекомендация: **shot-list** для прямого сравнения; Medium-66 — опционально.
- **K (повторы):** 1 или 3? (×стоимость).
- **Таймаут:** 660 (как эталон) или 1800 (безопаснее для medium)?
- **Регистрировать ли новый «профиль»** на fork-results-странице и в Workboard/эпике?

## 8. Рекомендация (пересмотрена после проверки)

~~Запустить одиночный прогон shot-list на `medium`…~~ — **невыполнимо через dsh**
(§ «ИТОГ ПРОВЕРКИ»). Вместо этого — §10.

## 10. Что реально можно сделать

1. **dsh + `off`** — единственный рабочий уровень для этой модели (эталон 51/52 уже есть).
   Перезапуск на `off` не нужен.
2. **dsh + `medium`** — только если **переопределить каталог возможностей pi-ai**
   (заставить pi-ai считать, что модель поддерживает `medium`). Это правка
   конфигурации/каталога dsh — отдельная задача, вне harness-bench-fast, требует
   аккуратности (dsh сам решает, поддерживает ли модель effort).
3. **Обход через OpenClaw-харнесс** (`run_openclaw_bench.py --thinking medium`): сырой
   Cloud.ru API принимает `medium` (проверено), НО у OC есть свой краш на длинных
   задачах (`incomplete_turn`, PR #28). То есть `medium` достижим на OC, но не на dsh.
4. **Другая модель** того же провайдера, где pi-ai заявляет поддержку `medium`.

Итог: **для dsh × DeepSeek-V4.1-Flash уровень `medium` недостижим** без правки
каталога pi-ai. Ответ на исходный вопрос — отрицательный, с доказательством.

## 9. Definition of Done

- [ ] Артефакт `results/dsh_shotlist_ds41flash_medium_<date>.json` записан, `thinking: medium`.
- [ ] Сравнение с `off`: pass-rate, время, шаги, токены/₽.
- [ ] Строка «dsh × ds41flash × medium» видна на fork-results (если нужен профиль).
- [ ] Нюансы (таймаут/403) зафиксированы в отчёте.
