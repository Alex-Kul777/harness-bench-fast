# result-reporting (delta)

## ADDED Requirements

### Requirement: Детализация для всех наших наборов

Все наши строки на `docs/fork.html` (Shot List, Light, Medium) SHALL иметь доступную
страницу детализации прогона и быть кликабельными. Для Medium SHALL использоваться
`docs/fork-run-<id>.html`; для Shot List и Light — `docs/fork-detail-<stem>.html`
(генератор `scripts/build_fork_home.py`). Страница детализации SHALL показывать сводку
прогона и таблицу задач (результат, секунды, токены, сообщение).

#### Scenario: Клик открывает детализацию любого набора

- **WHEN** пользователь кликает по нашей строке в любом наборе
- **THEN** SHALL открываться страница детализации этого прогона
  (`fork-run-<id>.html` для Medium, `fork-detail-<stem>.html` для Shot List/Light)

#### Scenario: Детализация показывает задачи

- **WHEN** открыта страница детализации
- **THEN** SHALL присутствовать сводка (Profile/Version/Result/Time/Steps/Tokens) и
  таблица задач с результатом, секундами, токенами и сообщением

#### Scenario: Отсутствие коллизии генераторов

- **WHEN** запускается `scripts/build_fork_pages.py`
- **THEN** страницы `docs/fork-detail-*.html` SHALL NOT удаляться (отдельный префикс)
