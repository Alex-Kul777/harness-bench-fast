# Proposal: refine-guidance-antipatterns

## Why

После публикации результатов новых моделей Cloud.ru (Shot List 52, Medium-66) в
`docs/model-selection-guidance.*` накопились расхождения между данными и нарративом,
а секция anti-patterns не показывает доминируемые строки новых моделей:

- TL;DR разрастался отдельными датированными буллетами по харнессам (Pi/dsh/OpenClaw/M66);
- факт «впервые пробит long-context» и вывод «52 ≠ 66 (depth)» не были выделены;
- секция «Как читать» не покрывала сценарий «долгие/глубокие задачи»;
- заголовок бакета `Medium · long (20)` показывал полный размер набора, хотя измерено 6;
- секция anti-patterns ограничивалась premium-моделями, поэтому доминируемые строки
  новых моделей (напр. `Kimi-K3` feasibility 39/40 @49.99₽ против DeepSeek 39/40 @12.68₽)
  в неё не попадали.

## What Changes

1. `docs/model-selection-guidance.{md,en.md}` (+ сгенерированные `.html`): TL;DR — один
   сводный блок «Cloud.ru batch — новые модели» + мини-таблица «52 vs 66 (depth)»;
   секция «Как читать» — добавлен сценарий «долгие/глубокие многошаговые задачи».
2. `scripts/build_model_selection.py`:
   - секция anti-patterns SHALL включать доминируемые строки из watchlist новых моделей
     (не только premium), MD- и HTML-рендеры SHALL использовать один предикат;
   - метка бакета long-context SHALL показывать измеренный знаменатель (`6/20`), когда он
     меньше полного набора.

## Out of scope

- Изменение методики подсчёта Pareto/тиров; пересчёт ₽/решений.
- Прогоны новых задач/моделей.

## Tracking

- Workboard: (project-a) `refine-guidance-antipatterns`
- Follow-up к Epic Alex-Kul777/openclaw-workspace#463 (Medium-66 Cloud.ru batch).
