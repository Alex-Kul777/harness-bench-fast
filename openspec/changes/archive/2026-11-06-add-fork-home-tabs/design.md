# add-fork-home-tabs — design

## Табы (progressive enhancement)
- Разметка: `.suite-switch` (кнопки) + `<section data-suite-panel="...">` (все видимы без JS).
- JS (inline): по клику активирует панель (`p.hidden`), `aria-pressed`, обновляет `location.hash`.
- При загрузке: читает hash; `#light`/`#medium` (наши редиректы) активируют нужный таб, иначе первый.

## Колонки
Ровно 9: `Harness · Profile · Model · Result · % · Time · Steps · Tokens (cost) · Version`.
`Source` из таблиц убран; `ours`/`upstream` — групповые строки (`tr.group`).

## Medium-волны
Поле `waves` в JSON строки Medium; под таблицей — `<details class="wave-breakdown">`
с конфигурациями × (Long/Reflect/Feasibility), прочерк при отсутствии.

## Безопасность
Все динамические значения — `html.escape`.

## Supersedes
Уточняет требование «Единая форк-страница» из `add-fork-home-page` (табы + 9 колонок).
