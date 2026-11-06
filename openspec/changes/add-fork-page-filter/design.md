# add-fork-page-filter — design

## Разметка
```html
<div class="filters">
  <label class="search">Search model or harness
    <input id="search" type="search" placeholder="e.g. Pi, OpenClaw, DeepSeek" autocomplete="off">
  </label>
  <span id="row-count" aria-live="polite"></span>
</div>
...
<p id="empty" role="status" hidden>No rows match your search.</p>
```

## Поведение (inline-JS)
- Фильтр применяется к строкам **главной** таблицы активной панели (не к волновой `<details>`).
- Совпадение — подстрока (case-insensitive) по `textContent` строки (харнесс+профиль+модель+версия).
- Групповые строки (`tr.group`) скрываются, если в группе не осталось видимых строк.
- `#row-count`: «N rows» без запроса, «N match(es)» с запросом; `#empty` видно только при 0 совпадений.
- Переприменяется при `activate()` (смена таба) и по `input`.

## JS-off / progressive enhancement
Без JS все строки видны (фильтр — надстройка). Безопасность: значения статические (экранированы генератором).

## Supersedes
Дополняет требование «Единая форк-страница» (табы + 9 колонок).
