# ADR-0006: Model & harness selection guidance — architecture

Date: 2026-11-15
Status: accepted
Deciders: gateway-owner, project-a-agent
Source: grilling session (grill-with-docs), Round 1

## Context

Пользователи выбирают модель/харнесс без обоснования, часто беря дорогие модели там,
где дешёвая даёт тот же результат. У репозитория ~120 прогонов и публичный форк-слой,
но нет слоя рекомендаций «что × чем × когда». Нужен evidence-based слой, опирающийся
только на уже выполненные прогоны, поверх существующих доменных доков
(`GLOSSARY.md` + `docs/adr/`).

## Decision

Строим слой рекомендаций как отдельный deliverable в ветке
`research/model-selection-guidance`:

1. **Форма.** Публичная `docs/model-selection-guidance.md` (+ `.en.md`) и
   машиночитаемая `model-selection-matrix.json`; на `fork.html` — компактная секция.
2. **Оси ситуации.** Класс сложности (Shot List / Medium / long) и wave/категория —
   основные; бюджет — ограничение (ceiling); «типовые задачи» — производная от wave.
3. **Оправданность premium.** База — фронт Парето (pass ↑, ₽ ↓) плюс объяснение через
   floor/boundary-задачи, которые дешёвые конфигурации не берут; иначе — anti-pattern.
4. **Харнесс.** Рекомендация — пара (harness × model), т.к. одна модель даёт разный
   score на Pi / OpenClaw / Hermes.
5. **Сопоставимость.** Сравнение только в одной task-set версии и протоколе;
   partial-покрытие = `unmeasured`, не fail; каждая рекомендация несёт флаг уверенности.
6. **Поддержка.** Гибрид: числа/матрицу генерирует `scripts/build_model_selection.py`
   с гейтами `--check/--lint` (по образцу fork-генераторов); нарратив «когда» — вручную.
7. **Routing.** Сейчас публикуем публичную страницу; routing policy для OpenClaw
   Dynamic Routing/Fallbacks — отдельный драфт (требует порогов бюджета от владельца).

## Consequences

- (+) Рекомендации воспроизводимы и проверяемы гейтами; числа не расходятся с `results/*.json`.
- (+) Слой отделён от канонического `GLOSSARY.md` — конфликты мержей минимальны
  (fork-doc-layering).
- (+) Anti-patterns дают прямой ответ на «почему не надо дорогую модель здесь».
- (−) Требует поддержки генератора и классификатора; риск «published nothing» при
  незарегистрированном прогоне (см. `Suite registration` в GLOSSARY).
- (−) Routing policy отложен → до его появления рекомендации не автоматизированы.
- (риск) Несопоставимые task-set версии могут дать ложные выводы, если флаг уверенности
  проигнорирован.

## Follow-ups

- Round 2 grilling: шаблон страницы, тир-лейблы/пороги, situation-buckets, version scope,
  порог premium, budget ceiling, схема JSON.
- `CONTEXT.md` (branch root) — живой глоссарий слоя рекомендаций.
