# version-fork-page-assets — tasks

## 1. Правка страницы

- [ ] 1.1 `docs/fork-medium90.html`: добавить `?v=` к `landing.css` и `fork-results.js`

## 2. Спека

- [ ] 2.1 Delta `result-reporting`: ADDED «Версионирование ассетов страницы»

## 3. QA / верификация

- [ ] 3.1 Локально: теги содержат `?v=`
- [ ] 3.2 После пуша: live-страница отдаёт теги с `?v=`
- [ ] 3.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
