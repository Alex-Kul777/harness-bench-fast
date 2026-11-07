<!-- Fork results (EN): Detailed fork-scoped benchmark tables for Alex-Kul777/harness-bench-fast.
     Russian-first document. Auto-generated block is rebuilt by scripts/build_fork_results.py. -->

# Форк-результаты `harness-bench-fast`

Детальные таблицы **нашего** форк-слоя. Обзор и главные цифры — в [`../FORK.md`](../FORK.md).
Upstream-методика и upstream-строки — в [`../README.md`](../README.md).

> **EN:** This file holds the fork's own results (Pi / OpenClaw / Hermes harnesses, wave 19).
> Russian-first; see `../FORK.md` for the short index.

## Содержание
- [Сводная таблица (автосинк)](#сводная-таблица-автосинк)
- [Shot List (52 задачи) — наши строки](#shot-list-52-задачи--наши-строки)
- [Wave 19 (432–471) — наш прогон](#wave-19-432471--наш-прогон)
- [Полные Light-прогоны (391)](#полные-light-прогоны-391)
- [Артефакты и протоколы](#артефакты-и-протоколы)

---

## Сводная таблица (автосинк)

Блок ниже **генерируется** скриптом `scripts/build_fork_results.py` из `results/*.json`.
Руками не редактировать — правь скрипт/JSON и пересобирай.

<!-- FORK:RESULTS:BEGIN -->
Автосинк: 19 прогонов

| Harness | Suite | Profile | Model | Result | % | Time | Steps | Tokens (cost) |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Hermes | Shot List (52) | thinking: off | GLM-5.2 (thinking: off) | 46/52 | 88.5% | 68.5m | — | 6 209 159 (1 509₽) |
| Hermes | Shot List (52) | — | GPT-OSS-120B | 28/52 | 53.8% | 37.9m | 427 | 8 833 747 (2 171₽) |
| Hermes | Shot List (52) | — | Qwen3.6-35B-A3B | 36/52 | 69.2% | 38.6m | 301 | 6 961 237 (1 737₽) |
| Hermes | Light (391) | — | — | 387/391 | 99.0% | 404.6m | — | 31 770 687 (7 775₽) |
| OpenClaw | Shot List (52) | — | DeepSeek-V4.1-Flash | 50/52 | 96.2% | 47.3m | — | 2 814 749 (165₽) |
| OpenClaw | Shot List (52) | thinking: off | GLM-5.2 (thinking: off) | 47/52 | 90.4% | 231.9m | — | 1 777 320 (1 793₽) |
| OpenClaw | Shot List (52) | — | GLM-5.3 | 44/52 | 84.6% | 46.1m | — | 1 955 767 (66₽) |
| OpenClaw | Shot List (52) | — | GPT-OSS-120B | 17/52 | 32.7% | 205.2m | — | 1 261 870 (1 080₽) |
| OpenClaw | Shot List (52) | — | Qwen3.6-35B-A3B | 40/52 | 76.9% | 195.2m | — | 2 109 433 (2 859₽) |
| OpenClaw | Light (391) | — | — | 378/391 | 96.7% | 1473.3m | — | 0 (0₽) |
| Pi | Shot List (52) | — | DeepSeek-V4.1-Flash | 49/52 | 94.2% | 21.3m | 330 | 1 438 179 (—) |
| Pi | Shot List (52) | thinking: off | GLM-5.2 (thinking: off) | 49/52 | 94.2% | 102.8m | 388 | 1 913 439 (501₽) |
| Pi | Shot List (52) | — | GLM-5.3 | 49/52 | 94.2% | 64.9m | 349 | 1 764 093 (216₽) |
| Pi | Shot List (52) | — | GigaChat 3 Pro | 16/52 | 30.8% | 25.7m | 2 034 | 12 883 705 (230₽) |
| Pi | Shot List (52) | — | Qwen3.6-35B-A3B | 42/52 | 80.8% | 18.5m | 327 | 1 318 346 (362₽) |
| Pi | Medium (392-471) | — | DeepSeek-V4.1-Flash | 11/15 | 73.3% | 137.3m | 1 124 | 15 124 377 (1 055₽) |
| Pi | Medium (392-471) | — | DeepSeek-V4.1-Flash | 5/5 | 100.0% | 32.0m | 336 | 2 949 354 (268₽) |
| Pi | Medium (392-471) | — | DeepSeek-V4.1-Flash | 0/3 | 0.0% | 288.7m | 1 650 | 78 233 678 (2 799₽) |
| — | Wave 19 (40) | — | DeepSeek-V4.1-Flash | 36/40 | 90.0% | 174.8m | 2 748 | 48 463 320 (3 923₽) |
<!-- FORK:RESULTS:END -->

---

## Shot List (52 задачи) — наши строки

Стратифицированная выборка 52 задач (~13% от 391). Полная таблица (вместе с upstream)
— в [`README.md`](../README.md#shot-list-leaderboard-52-tasks). Здесь только наши прогоны.
`Время` — wall-clock минуты; `Стоимость` — оценка расхода в ₽.

| Harness | Profile | Model | Result | % | Time | Steps | Tokens (cost) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| OpenClaw | thinking: off (2026-11-04) | DeepSeek-V4.1-Flash | 50/52 | 96.2% | 47.3m | 237 | 2 814 749 (165₽) |
| Pi | — (2026-11-04) | DeepSeek-V4.1-Flash | 49/52 | 94.2% | 21.4m | 330 | 1 438 179 (~150₽) |
| Pi | — (2026-11-04) | GLM-5.3 | 49/52 | 94.2% | 64.9m | 349 | 1 764 093 (~220₽) |
| Pi | thinking: off (2026-08-17) | GLM-5.2 | 49/52 | 94.2% | 102.8m | 388 | 1 913 439 (501₽) |
| Hermes | MCP off (2026-08-10) | GLM-5.2 | 48/52 | 92.3% | 93.1m | 953 | 11 442 855 |
| OpenClaw | thinking: off (2026-08-12) | GLM-5.2 | 47/52 | 90.4% | 231.9m | 247 | 1 777 320 (1 793₽) |
| OpenClaw | thinking: high (2026-08-10) | GLM-5.2 | 46/52 | 88.5% | 226.4m | — | — |
| Hermes | MCP off + thinking: off (2026-08-13) | GLM-5.2 | 46/52 | 88.5% | 68.5m | 270 | 6 209 159 (1 509₽) |
| OpenClaw | thinking: off (2026-11-04) | GLM-5.3 | 44/52 | 84.6% | 46.1m | — | 1 955 767 (~50₽+) |
| Pi | — (2026-08-17) | Qwen3.6-35B-A3B | 42/52 | 80.8% | 18.5m | 327 | 1 318 346 (362₽) |
| OpenClaw | — (2026-08-17) | Qwen3.6-35B-A3B | 40/52 | 76.9% | 195.2m | 328 | 11 672 005 (2 859₽) |
| Hermes | — (2026-08-17) | Qwen3.6-35B-A3B | 36/52 | 69.2% | 38.6m | 301 | 6 961 237 (1 737₽) |
| Hermes | — (2026-08-13) | GPT-OSS-120B | 28/52 | 53.8% | 37.9m | 427 | 8 833 747 (2 171₽) |
| OpenClaw | thinking: off (2026-08-13) | GPT-OSS-120B | 17/52 | 32.7% | 205.2m | 120 | 1 261 870 (1 080₽) |
| Pi | — (2026-11-07) | GigaChat 3 Pro | 16/52 | 30.8% | 25.7m | 2034 | 12 883 705 (230₽) |

## Wave 19 (432–471) — наш прогон

Wave 19 — 40 задач в 20 парах (feasibility). Наш замер — Pi + DeepSeek V4.1 Flash.

| Harness | Profile | Model | Result | % | Time | Steps | Tokens (cost) | Источник |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **Pi** | — | DeepSeek V4.1 Flash | **36/40** | **90.0%** | 174.8m | 2 748 | 48 463 320 (3 923₽) | `runs/pi_deepseek_v41flash_wave19_20261104.json` |
| Codex CLI 0.160.1 | reasoning: high | DeepSeek V4.1 Flash | 31/40 | 77.5% | — | — | — | upstream |
| Claude Code 2.1.300 | reasoning: high | DeepSeek V4.1 Flash | 30/40 | 75.0% | — | — | — | upstream |
| OpenClaw 2026.9.6 | reasoning: high | DeepSeek V4.1 Flash | 28/40 | 70.0% | — | — | — | upstream |
| DeepAgents (previous full run) | reasoning: high | DeepSeek V4.1 Flash | 27/40 | 67.5% | — | — | — | upstream |
| pi-mono 0.73.1 | reasoning: high | DeepSeek V4.1 Flash | 26/40 | 65.0% | — | — | — | upstream |

Детали прогона: k=1, 94 мин, 2 748 шагов, 2 238 tool-calls,
9.57M вход + 2.17M выход (вкл. 1.44M reasoning), ≈3 923 ₽; инфраструктурных сбоев нет.
Разрыв **+10/40 над upstream pi-mono (26/40)** — provisional, не валидирован.

Небольшой smoke/sample для волны: `results/sample_wave19.json` (5/5), `results/smoke_wave_reflect.json` (1/1).

## Полные Light-прогоны (391)

Наши полные прогоны Light (задачи 1–391). Значения — из наших JSON; это **не** пересчёт
upstream-таблицы.

| Harness | Profile | Model | Result | % | Time | Steps | Tokens (cost) | JSON |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Hermes | MCP off | GLM-5.2 | 387/391 | 99.0% | 404.6m | — | 31 770 687 (7 775₽) | `results/hermes_full_391.json` |
| Pi | high | GLM-5.2 | 385/391 | 98.5% | — | — | — | `runs/pi_glm52_high_full391_v016.json` |
| OpenClaw | — | GLM-5.2 | 378/391 | 96.7% | 1473.3m | — | 0 (0₽) | `results/oc_full_391.json` |
| Hermes | MCP off | GLM-5.2 | — | — | — | — | — | `runs/hermes_glm52_mcpoff_full391_v016.json` |
| OpenClaw | — | GLM-5.2 | — | — | — | — | — | `runs/openclaw_glm52_full391_v016.json` |

> Прочерк — прогон сохранён как сырой `runs/*_v016.json`; актуальная сводка берётся из `results/`.

## Артефакты и протоколы

| Что | Где |
| --- | --- |
| Shot-list JSON (наши) | `results/{pi,oc,hermes}_shotlist_*.json` |
| Shot-list HTML | `docs/{oc,hermes}_shotlist_*.html`, `docs/oc_shotlist_thinking_off.html` |
| Wave 19 | `results/wave19_full_ds41flash.json`, `results/sample_wave19.json` |
| Wave 19 диагностика | `results/diag_wave19.json`, `results/diag_wave19_fixc.json` |
| Light (391) JSON | `results/{glm52,hermes,oc}_full_391.json`, `runs/*_full391_v016.json` |
| Доки форка | `docs/adr/0001-shot-list.md`, `GLOSSARY.md` |
| Скилл | `.agents/skills/harness-bench-fast/SKILL.md` |

**Merge-guard.** При конфликте с upstream эти файлы — «keep ours». Основной `README.md`
содержит только короткий баннер между `<!-- FORK:BEGIN -->` и `<!-- FORK:END -->`.
Скрипт пересборки: `python3 scripts/build_fork_results.py`.
