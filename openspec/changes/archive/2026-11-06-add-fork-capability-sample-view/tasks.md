# add-fork-capability-sample-view — tasks

## 1. Генератор

- [x] 1.1 Читать `docs/fork-sample-manifest.json`
- [x] 1.2 Собирать результаты по allow-list `SAMPLE_SOURCES` (long/reflect/feasibility) из `results/`
- [x] 1.3 Помечать long как `invalid` (reason `timeout 2400 < wave floor 7200`)
- [x] 1.4 Писать `docs/fork-sample-results.json` по схеме
- [x] 1.5 Генерировать `docs/fork-sample.html` (summary + per-task + note/details), экранировать

## 2. Интеграция

- [x] 2.1 Ссылка «Capability sample (20)» в nav `docs/fork-medium90.html`

## 3. Спека

- [x] 3.1 Delta `result-reporting`: ADDED «Вид capability-сэмпла»

## 4. QA / верификация

- [x] 4.1 Генерация → оба файла; `--check` → 0
- [x] 4.2 Страница: 20 задач, long invalid, feasibility 12
- [x] 4.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0
- [x] 4.4 Live: `fork-sample.html` 200 (Pages переведён на GitHub Actions)
