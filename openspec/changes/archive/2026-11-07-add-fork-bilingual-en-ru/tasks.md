# add-fork-bilingual-en-ru — tasks

## 1. Каталог локалей

- [x] 1.1 `scripts/fork_i18n.py`: `CATALOG {ru, en}` + helper `t(locale, key)` с fallback на `ru`
- [x] 1.2 Тест: ключи симметричны (ru/en); пропущенный ключ откатывается на дефолт
- [x] 1.3 Тест: неизвестная локаль → дефолт

## 2. Генератор единой страницы (`build_fork_home.py`)

- [x] 2.1 Параметр локали; тексты из каталога (title, nav, intro, табы+подписи, поиск, групповые строки, notes, fine-print, footer)
- [x] 2.2 RU-дефолт `docs/fork.html` без изменений семантики; EN-зеркало `docs/fork.en.html`
- [x] 2.3 EN-зеркала `docs/fork-sample.en.html` и `docs/fork-detail-<stem>.en.html`
- [x] 2.4 Языковой переключатель в nav (сохраняет `#hash`/таб)
- [x] 2.5 `--check` покрывает RU и EN файлы

## 3. Генератор страниц/деталей (`build_fork_pages.py`)

- [x] 3.1 Локаль + EN-зеркала `docs/fork-run-<id>.en.html`
- [x] 3.2 Legacy-redirect (`fork-medium90.html`, `fork-light.html`) не ломается
- [x] 3.3 `--check` покрывает EN-зеркала

## 4. Генератор авто-блока (`build_fork_results.py`)

- [x] 4.1 EN-зеркало `docs/fork-results.en.md`; авто-блок с EN-подписями групп
- [x] 4.2 `FORK.en.md` (EN-зеркало RU- `FORK.md`) + ссылки-переключатели в обоих
- [x] 4.3 `--check`/`--lint` покрывают EN-файл (колонки канонические — английские)

## 5. Спека

- [x] 5.1 New capability `localization` (локаль-политика, каталог, переключатель, паритет)
- [x] 5.2 Delta `result-reporting`: ADDED «Двуязычные страницы результатов» + «Двуязычный авто-блок»

## 6. QA / верификация

- [x] 6.1 `build_fork_results.py --check`/`--lint`, `build_fork_home.py --check`, `build_fork_pages.py --check` → 0 (RU + EN)
- [x] 6.2 Паритет локалей: строки данных RU == EN (тест `tests/test_fork_bilingual.py`)
- [x] 6.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [x] 6.4 Без JS: RU-страница читается целиком (все строки видны)
- [x] 6.5 Live: `fork.html` и `fork.en.html` → 200; переключение локали сохраняет таб (`#medium`)

## 7. Архивация

- [x] 7.1 `openspec archive add-fork-bilingual-en-ru` после полного выполнения и verify
- [x] 7.2 Обновить merge-guard заметки/скилл `fork-doc-layering` при необходимости
