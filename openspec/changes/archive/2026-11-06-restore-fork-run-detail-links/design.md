# restore-fork-run-detail-links — design

## Разметка
Строка с `detail` (относительный URL детализации, напр. `fork-run-pi-deepseek-v4-1-flash.html`):
```html
<tr class="detail-row" data-detail="fork-run-pi-deepseek-v4-1-flash.html">
  <td><a href="fork-run-....html">Pi</a></td> ...
</tr>
```

## JS
Клик по строке `tr[data-detail]` (кроме клика по ссылке) → `location.href = data-detail`.
Курсор pointer, hover-подсветка.

## Источник
`docs/fork-medium90-results.json` → `rows[].details_url` (наши Medium-конфиги).
Страницы детализации генерирует `scripts/build_fork_pages.py`.

## Примечание
Детализация существует только там, где есть `fork-run-*` страница (сейчас — Medium).
Остальные строки остаются некликабельными.
