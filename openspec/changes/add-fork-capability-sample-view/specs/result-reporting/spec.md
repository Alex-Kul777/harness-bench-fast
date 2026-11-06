# result-reporting (delta)

## ADDED Requirements

### Requirement: Вид capability-сэмпла

Форк SHALL публиковать cost-bounded capability sample (20 задач = 25% Medium) отдельным
видом: `docs/fork-sample.html` + данные `docs/fork-sample-results.json`, собранные из
манифеста `docs/fork-sample-manifest.json`. Волна long SHALL помечаться `invalid`, если её
таймаут был ниже флора волны.

#### Scenario: Генерация вида

- **WHEN** запускается `python3 scripts/build_fork_pages.py`
- **THEN** SHALL создаваться `docs/fork-sample-results.json` и `docs/fork-sample.html`
  по задачам манифеста

#### Scenario: Невалидная волна помечена

- **WHEN** волна long измерена с таймаутом ниже флора (7200)
- **THEN** её статус SHALL отображаться как `invalid` с причиной, а не как обычный fail

#### Scenario: Ссылка на манифест

- **WHEN** страница сэмпла отображается
- **THEN** она SHALL содержать ссылку на `docs/fork-sample-manifest.json`
