<!-- Fork results (EN): Detailed fork-scoped benchmark tables for Alex-Kul777/harness-bench-fast.
     English mirror of docs/fork-results.md. Auto-generated block is rebuilt by scripts/build_fork_results.py. -->

# Fork results · `harness-bench-fast`

Detailed tables for **our** fork layer. Overview and headline numbers live in [`../FORK.md`](../FORK.md) (RU) / [`../FORK.en.md`](../FORK.en.md) (EN).
Upstream methodology and upstream rows stay in [`../README.md`](../README.md).

> **RU:** Это зеркало русскоязычного файла [`fork-results.md`](fork-results.md). RU-версия — дефолт.

Our **Medium** sets live on the single fork page:
[`docs/fork.html#medium`](fork.html#medium) — the full **90** tasks (with a `partial` marker for
incomplete coverage) and [`docs/fork.html#medium-sample`](fork.html#medium-sample) — the truncated
**sample** (our 66 coverage + pilot 13; pilot: [`docs/fork-medium-pilot-manifest.json`](fork-medium-pilot-manifest.json)).

## Contents
- [Summary table (auto-sync)](#summary-table-auto-sync)
- [Shot List (52 tasks) — our rows](#shot-list-52-tasks--our-rows)
- [Wave 19 (432–471) — our run](#wave-19-432471--our-run)
- [Full Light runs (391)](#full-light-runs-391)
- [Artifacts and protocols](#artifacts-and-protocols)

---

## Summary table (auto-sync)

The block below is **generated** by `scripts/build_fork_results.py` from `results/*.json`.
Do not edit by hand — change the script/JSON and rebuild.

<!-- FORK:RESULTS:BEGIN -->
Auto-sync: 38 runs

| Harness | Suite | Profile | Model | Result | % | Time | Steps | Tokens (cost) |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Hermes | Shot List (52) | thinking: off | GLM-5.2 (thinking: off) | 46/52 | 88.5% | 68.5m | — | 6 209 159 (1 509₽) |
| Hermes | Shot List (52) | — | GPT-OSS-120B | 28/52 | 53.8% | 37.9m | 427 | 8 833 747 (2 171₽) |
| Hermes | Shot List (52) | — | Qwen3.6-35B-A3B | 36/52 | 69.2% | 38.6m | 301 | 6 961 237 (1 737₽) |
| Hermes | Light (391) | — | — | 387/391 | 99.0% | 404.6m | — | 31 770 687 (7 775₽) |
| OpenClaw | Shot List (52) | — | DeepSeek-V4.1-Flash | 50/52 | 96.2% | 47.3m | 237 | 2 814 749 (123₽) |
| OpenClaw | Shot List (52) | thinking: high | DeepSeek-V4.1-Flash (thinking: high) | 51/52 | 98.1% | 40.3m | 244 | 2 926 226 (38₽) |
| OpenClaw | Shot List (52) | thinking: medium | DeepSeek-V4.1-Flash (thinking: medium) | 52/52 | 100.0% | 40.6m | 224 | 2 935 013 (39₽) |
| OpenClaw | Shot List (52) | thinking: off | DeepSeek-V4.1-Flash (thinking: off) | 50/52 | 96.2% | 37.9m | 244 | 2 718 375 (35₽) |
| OpenClaw | Shot List (52) | thinking: off | GLM-5.2 (thinking: off) | 47/52 | 90.4% | 231.9m | 247 | 1 777 320 (1 302₽) |
| OpenClaw | Shot List (52) | — | GLM-5.3 | 44/52 | 84.6% | 46.1m | 148 | 1 955 767 (50₽) |
| OpenClaw | Shot List (52) | — | GPT-OSS-120B | 17/52 | 32.7% | 205.2m | 120 | 1 261 870 (786₽) |
| OpenClaw | Shot List (52) | — | Qwen3.6-35B-A3B | 40/52 | 76.9% | 195.2m | 328 | 2 109 433 (2 079₽) |
| OpenClaw | Light (391) | — | — | 378/391 | 96.7% | 1473.3m | — | 0 (0₽) |
| OpenClaw | Medium (392-471) | thinking: high | DeepSeek-V4.1-Flash (thinking: high) | 38/40 | 95.0% | 105.0m | 783 | 25 623 769 (371₽) |
| OpenClaw | Medium (392-471) | thinking: high | DeepSeek-V4.1-Flash (thinking: high) | 17/20 | 85.0% | 81.5m | 406 | 14 660 719 (195₽) |
| OpenClaw | Medium (392-471) | thinking: medium | DeepSeek-V4.1-Flash (thinking: medium) | 39/40 | 97.5% | 123.7m | 811 | 24 275 573 (363₽) |
| OpenClaw | Medium (392-471) | thinking: medium | DeepSeek-V4.1-Flash (thinking: medium) | 16/20 | 80.0% | 69.1m | 399 | 11 144 179 (183₽) |
| OpenClaw | Medium (392-471) | thinking: off | DeepSeek-V4.1-Flash (thinking: off) | 36/40 | 90.0% | 169.6m | 873 | 29 641 266 (407₽) |
| OpenClaw | Medium (392-471) | thinking: off | DeepSeek-V4.1-Flash (thinking: off) | 12/20 | 60.0% | 128.5m | 467 | 10 009 328 (161₽) |
| OpenClaw | Medium (392-471) | thinking: off | DeepSeek-V4.1-Flash (thinking: off) | 0/2 | 0.0% | 45.6m | 4 | 9 429 226 (152₽) |
| Pi | Shot List (52) | — | DeepSeek-V4.1-Flash | 49/52 | 94.2% | 21.3m | 330 | 1 438 179 (34₽) |
| Pi | Shot List (52) | thinking: off | GLM-5.2 (thinking: off) | 49/52 | 94.2% | 102.8m | 388 | 1 913 439 (501₽) |
| Pi | Shot List (52) | — | GLM-5.3 | 49/52 | 94.2% | 64.9m | 349 | 1 764 093 (216₽) |
| Pi | Shot List (52) | — | GigaChat 3 Pro | 16/52 | 30.8% | 25.7m | 2 034 | 12 883 705 (230₽) |
| Pi | Shot List (52) | thinking: high | GigaChat 3.5 Reasoning (thinking: high) | 34/52 | 65.4% | 33.8m | 1 160 | 3 796 473 (159₽) |
| Pi | Shot List (52) | thinking: low | GigaChat 3.5 Reasoning (thinking: low) | 35/52 | 67.3% | 15.8m | 1 116 | 3 041 748 (139₽) |
| Pi | Shot List (52) | thinking: medium | GigaChat 3.5 Reasoning (thinking: medium) | 34/52 | 65.4% | 19.2m | 1 176 | 2 974 629 (150₽) |
| Pi | Shot List (52) | — | Qwen3.6-35B-A3B | 42/52 | 80.8% | 18.5m | 327 | 1 318 346 (362₽) |
| Pi | Medium (392-471) | — | DeepSeek-V4.1-Flash | 11/15 | 73.3% | 137.3m | 1 124 | 15 124 377 (278₽) |
| Pi | Medium (392-471) | — | DeepSeek-V4.1-Flash | 5/5 | 100.0% | 32.0m | 336 | 2 949 354 (71₽) |
| Pi | Medium (392-471) | — | DeepSeek-V4.1-Flash | 0/3 | 0.0% | 288.7m | 1 650 | 78 233 678 (744₽) |
| Pi | Medium (392-471) | — | GigaChat 3 Pro | 0/40 | 0.0% | 15.0m | 1 408 | 27 408 162 (801₽) |
| Pi | Medium (392-471) | — | GigaChat 3 Pro | 0/6 | 0.0% | 23.5m | 1 020 | 22 942 929 (299₽) |
| Pi | Medium (392-471) | — | GigaChat 3 Pro | 0/20 | 0.0% | 31.6m | 2 948 | 25 638 927 (316₽) |
| Pi | Medium (392-471) | thinking: low | GigaChat 3.5 Reasoning (thinking: low) | 11/40 | 27.5% | 517.1m | 2 973 | 94 222 758 (1 740₽) |
| Pi | Medium (392-471) | thinking: low | GigaChat 3.5 Reasoning (thinking: low) | 2/20 | 10.0% | 210.9m | 2 176 | 31 410 934 (511₽) |
| Pi | Medium (392-471) | thinking: low | GigaChat 3.5 Reasoning (thinking: low) | 0/6 | 0.0% | 62.2m | 1 419 | 65 534 148 (456₽) |
| — | Wave 19 (40) | — | DeepSeek-V4.1-Flash | 36/40 | 90.0% | 174.8m | 2 748 | 48 463 320 (1 045₽) |
<!-- FORK:RESULTS:END -->

---

## Shot List (52 tasks) — our rows

A stratified sample of 52 tasks (~13% of 391). The full table (with upstream) lives in
[`README.md`](../README.md#shot-list-leaderboard-52-tasks). Only our runs are shown here.
`Time` is wall-clock minutes; `Cost` is an estimated spend in roubles.

| Harness | Profile | Model | Result | % | Time | Steps | Tokens (cost) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| OpenClaw | thinking: medium (2026-11-07) | DeepSeek-V4.1-Flash | 52/52 | 100.0% | 40.6m | — | 2 935 013 (148₽) |
| OpenClaw | thinking: high (2026-11-07) | DeepSeek-V4.1-Flash | 51/52 | 98.1% | 40.3m | — | 2 926 226 (141₽) |
| OpenClaw | thinking: off (2026-11-07) | DeepSeek-V4.1-Flash | 50/52 | 96.2% | 37.9m | — | 2 718 375 (133₽) |
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

## Wave 19 (432–471) — our run

Wave 19 is 40 tasks in 20 pairs (feasibility). Our measurement is Pi + DeepSeek V4.1 Flash.

| Harness | Profile | Model | Result | % | Time | Steps | Tokens (cost) | Source |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **Pi** | — | DeepSeek V4.1 Flash | **36/40** | **90.0%** | 174.8m | 2 748 | 48 463 320 (3 923₽) | `runs/pi_deepseek_v41flash_wave19_20261104.json` |
| Codex CLI 0.160.1 | reasoning: high | DeepSeek V4.1 Flash | 31/40 | 77.5% | — | — | — | upstream |
| Claude Code 2.1.300 | reasoning: high | DeepSeek V4.1 Flash | 30/40 | 75.0% | — | — | — | upstream |
| OpenClaw 2026.9.6 | reasoning: high | DeepSeek V4.1 Flash | 28/40 | 70.0% | — | — | — | upstream |
| DeepAgents (previous full run) | reasoning: high | DeepSeek V4.1 Flash | 27/40 | 67.5% | — | — | — | upstream |
| pi-mono 0.73.1 | reasoning: high | DeepSeek V4.1 Flash | 26/40 | 65.0% | — | — | — | upstream |

Run details: k=1, 94 min, 2 748 steps, 2 238 tool-calls,
9.57M input + 2.17M output (incl. 1.44M reasoning), ≈3 923 ₽; no infrastructure failures.
The gap of **+10/40 over upstream pi-mono (26/40)** is provisional, not independently validated.

A small smoke/sample for the wave: `results/sample_wave19.json` (5/5), `results/smoke_wave_reflect.json` (1/1).

## Full Light runs (391)

Our full Light runs (tasks 1–391). Values come from our JSON; this is **not** a recomputation of
the upstream table.

| Harness | Profile | Model | Result | % | Time | Steps | Tokens (cost) | JSON |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Hermes | MCP off | GLM-5.2 | 387/391 | 99.0% | 404.6m | — | 31 770 687 (7 775₽) | `results/hermes_full_391.json` |
| Pi | high | GLM-5.2 | 385/391 | 98.5% | — | — | — | `runs/pi_glm52_high_full391_v016.json` |
| OpenClaw | — | GLM-5.2 | 378/391 | 96.7% | 1473.3m | — | 0 (0₽) | `results/oc_full_391.json` |
| Hermes | MCP off | GLM-5.2 | — | — | — | — | — | `runs/hermes_glm52_mcpoff_full391_v016.json` |
| OpenClaw | — | GLM-5.2 | — | — | — | — | — | `runs/openclaw_glm52_full391_v016.json` |

> A dash means the run is kept as a raw `runs/*_v016.json`; the current summary is taken from `results/`.

## Artifacts and protocols

| What | Where |
| --- | --- |
| Shot-list JSON (ours) | `results/{pi,oc,hermes}_shotlist_*.json` |
| Shot-list HTML | `docs/{oc,hermes}_shotlist_*.html`, `docs/oc_shotlist_thinking_off.html` |
| Wave 19 | `results/wave19_full_ds41flash.json`, `results/sample_wave19.json` |
| Wave 19 diagnostics | `results/diag_wave19.json`, `results/diag_wave19_fixc.json` |
| Light (391) JSON | `results/{glm52,hermes,oc}_full_391.json`, `runs/*_full391_v016.json` |
| Fork docs | `docs/adr/0001-shot-list.md`, `GLOSSARY.md` |
| Skill | `.agents/skills/harness-bench-fast/SKILL.md` |

**Merge guard.** On an upstream conflict these files are "keep ours". The main `README.md`
holds only a short banner between `<!-- FORK:BEGIN -->` and `<!-- FORK:END -->`.
Rebuild script: `python3 scripts/build_fork_results.py`.
