# add-fork-page-filter

## Why
Владелец хочет на `docs/fork.html` фильтр/поиск как на upstream-странице
(`Search model or harness`), чтобы быстро находить строку по модели/харнессу.

## What Changes
- `scripts/build_fork_home.py` → `docs/fork.html`: добавляется панель фильтра
  (`.filters`) с полем `Search model or harness` (`id="search"`), счётчиком
  `id="row-count"` (`aria-live`) и сообщением `id="empty"`.
- Inline-JS фильтрует строки **активного таба** по подстроке (модель/харнесс/профиль/версия),
  скрывает пустые групповые строки, обновляет счётчик и сообщение «нет совпадений».
- Фильтр переприменяется при переключении таба и сбрасывается при смене hash.

## Impact
- Только `scripts/build_fork_home.py` + `docs/fork.html`. Данные не меняются.
