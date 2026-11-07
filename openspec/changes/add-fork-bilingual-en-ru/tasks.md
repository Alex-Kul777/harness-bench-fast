# add-fork-bilingual-en-ru — tasks

## 1. Каталог локалей

- [ ] 1.1 `scripts/fork_i18n.py`: `CATALOG {ru, en}` + helper `t(locale, key)` с fallback на `ru`
- [ ] 1.2 Тест: ключи симметричны (ru/en); пропущенный ключ откатывается на дефолт
- [ ] 1.3 Тест: неизвестная локаль → дефолт

## 2. Генератор единой страницы (`build_fork_home.py`)

- [ ] 2.1 Параметр локали; тексты из каталога (title, nav, intro, табы+подписи, поиск, групповые строки, notes, fine-print, footer)
- [ ] 2.2 RU-дефолт `docs/fork.html` без изменений семантики; EN-зеркало `docs/fork.en.html`
- [ ] 2.3 EN-зеркала `docs/fork-sample.en.html` и `docs/fork-detail-<stem>.en.html`
- [ ] 2.4 Языковой переключатель в nav (сохраняет `#hash`/таб)
- [ ] 2.5 `--check` покрывает RU и EN файлы

## 3. Генератор страниц/деталей (`build_fork_pages.py`)

- [ ] 3.1 Локаль + EN-зеркала `docs/fork-run-<id>.en.html`
- [ ] 3.2 Legacy-redirect (`fork-medium90.html`, `fork-light.html`) не ломается
- [ ] 3.3 `--check` покрывает EN-зеркала

## 4. Генератор авто-блока (`build_fork_results.py`)

- [ ] 4.1 EN-зеркало `docs/fork-results.en.md`; авто-блок с EN-подписями групп
- [ ] 4.2 `FORK.en.md` (EN-зеркало RU- `FORK.md`) + ссылки-переключатели в обоих
- [ ] 4.3 `--check`/`--lint` покрывают EN-файл (колонки канонические — английские)

## 5. Спека

- [ ] 5.1 New capability `localization` (локаль-политика, каталог, переключатель, паритет)
- [ ] 5.2 Delta `result-reporting`: ADDED «Двуязычные страницы результатов» + «Двуязычный авто-блок»

## 6. QA / верификация

- [ ] 6.1 `build_fork_results.py --check`/`--lint`, `build_fork_home.py --check`, `build_fork_pages.py --check` → 0 (RU + EN)
- [ ] 6.2 Паритет локалей: строки данных RU == EN по каждому набору (тест/чек)
- [ ] 6.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [ ] 6.4 Без JS: RU-страница читается целиком (все строки видны)
- [ ] 6.5 Live: `fork.html` и `fork.en.html` → 200; переключение локали сохраняет таб (`#medium`)

## 7. Архивация

- [ ] 7.1 `openspec archive add-fork-bilingual-en-ru` после полного выполнения и verify
- [ ] 7.2 Обновить merge-guard заметки/скилл `fork-doc-layering` при необходимости
