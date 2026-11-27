## ADDED Requirements

### Requirement: Anti-patterns включают доминируемые новые модели

Секция anti-patterns руководства (`scripts/build_model_selection.py`) SHALL включать
доминируемые строки не только premium-лестницы, но и моделей из watchlist Cloud.ru batch
(`Kimi-K3`, `Gemini-3.8-Flash`, `GLM-5.3-FlashX`, `GPT-6.1-Sol`). Строка SHALL считаться
anti-pattern, WHEN она доминируема более дешёвой конфигурацией с тем же/лучшим результатом,
не singleton, имеет цену и измерена на полном сопоставимом наборе. MD- и HTML-рендеры
SHALL использовать один и тот же предикат отбора.

#### Scenario: Доминируемая новая модель попадает в anti-patterns

- **WHEN** строка `Kimi-K3` (feasibility 39/40 @49.99₽) доминируется `DeepSeek` (39/40 @12.68₽)
- **THEN** она SHALL появляться в секции anti-patterns, а не только в матрице

#### Scenario: Partial-набор не даёт anti-pattern

- **WHEN** строка измерена на partial-наборе (напр. long 6/20)
- **THEN** она SHALL NOT попадать в anti-patterns (остаётся `unmeasured`)

### Requirement: Метка partial long-бакета

Заголовок бакета long-context SHALL показывать измеренный знаменатель, WHEN он меньше
полного размера набора (напр. `Medium · long (6/20)`, а не `Medium · long (20)`).

#### Scenario: Частичное покрытие long

- **WHEN** в бакете long-context измерено 6 из 20 задач
- **THEN** метка бакета SHALL быть `Medium · long (6/20)`
