# add-fork-home-page — tasks

## 1. Генератор
- [x] 1.1 `scripts/build_fork_home.py`: читать наши Shot List / Light / Medium
- [x] 1.2 Upstream-строки Light из `docs/leaderboard-results.json`
- [x] 1.3 Писать `docs/fork-home-results.json` (схема из design.md)
- [x] 1.4 Генерировать `docs/fork.html` (единая схема, escape, секции-анкоры)

## 2. Интеграция
- [x] 2.1 Nav на `fork.html` со `fork-sample.html`
- [x] 2.2 Старые URL `fork-medium90.html` / `fork-light.html` → редирект-заглушки

## 3. Спека
- [x] 3.1 Delta `result-reporting`: ADDED «Единая форк-страница»

## 4. QA / верификация
- [x] 4.1 Генерация → оба файла; `--check` → 0
- [x] 4.2 3 секции, наши+upstream строки, колонка Version
- [x] 4.3 `openspec validate --all --strict` → 0
- [x] 4.4 Live: `fork.html` 200; старые URL не 404
