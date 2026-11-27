# Design: refine-guidance-antipatterns

## Decisions

- **D1 (anti-patterns watchlist).** Добавляем `ANTIPATTERN_EXTRA_LABELS = ("Kimi-K3",
  "Gemini-3.8-Flash", "GLM-5.3-FlashX", "GPT-6.1-Sol")` и предикат `_is_antipattern()` =
  premium ∪ watchlist. Доминирование по-прежнему требует полного сопоставимого набора
  (`coverage.full`) — partial-волны (long 6/20) остаются «unmeasured» и в anti-patterns
  не попадают.
- **D2 (единый предикат).** Ранее MD- и HTML-рендеры anti-patterns расходились (HTML
  требовал `coverage.full`, MD — нет). Приводим оба к одному предикату.
- **D3 (метка long-бакета).** `BUCKET_LABEL["long-context"]` динамически принимает
  `Medium · long (<measured>/20)`, когда измерено меньше полного набора.
- **D4 (нарратив).** TL;DR-буллеты консолидированы; HTML собирает TL;DR/How-to-read из
  `.md` (`_md_section_html`), поэтому правки MD достаточно.

## Risks

- Расширение anti-patterns добавляет строки и может вытеснить старые (лимит 12, dedup по
  модели). Приемлемо: секция — «не переплачивай», новые доминируемые строки практически
  значимы. Гейты `--check/--lint` зелёные.
