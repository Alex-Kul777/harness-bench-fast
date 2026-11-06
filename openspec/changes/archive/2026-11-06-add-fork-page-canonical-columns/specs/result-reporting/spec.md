# result-reporting (delta)

## MODIFIED Requirements

### Requirement: Страница-таблица результатов форка

Форк SHALL предоставлять статическую страницу `docs/fork-medium90.html`, которая
рендерит данные из `docs/fork-medium90-results.json` и содержит матрицу
**Harness × Wave** и per-config таблицу с 95% Wilson-интервалом. Per-config таблица
SHALL содержать канонические колонки форка `Profile` и `Tokens (cost)`.

#### Scenario: Отрисовка данных

- **WHEN** страница открывается в браузере
- **THEN** она SHALL отображать строки по конфигурациям и волнам, а неизмеренные волны
  помечать как `Unmeasured`, а не как `0/total`

#### Scenario: Колонка Profile

- **WHEN** per-config таблица отрисовывается
- **THEN** она SHALL содержать колонку `Profile`, показывающую `row.profile`, или `—`, если профиль не задан

#### Scenario: Колонка Tokens (cost) в рублях

- **WHEN** per-config таблица отрисовывается
- **THEN** колонка `Tokens (cost)` SHALL показывать токены и оценку стоимости в рублях (`₽`)
  из `row.usage.cost_rub`; при отсутствии стоимости SHALL показываться только токены
