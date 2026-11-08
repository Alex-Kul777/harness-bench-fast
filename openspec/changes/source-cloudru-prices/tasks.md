# Tasks: source-cloudru-prices

- [x] OpenSpec: proposal / design / tasks / spec-delta для `benchmark-runs`
- [x] `scripts/sync_cloudru_prices.py`: fetch каталога, кэш `{fetched_at, models}`,
      `--out`/`--ttl`, сохранение прежнего кэша при сетевой/HTTP-ошибке (exit != 0)
- [x] `harness_bench/cost_resolver.py`: precedence cache > config > fallback,
      `cache_read` отсутствует → 0, публичный API сохранён
- [x] `tests/test_cloudru_prices.py`: парсинг каталога (mock httpx), кэш + TTL,
      precedence, значения GigaChat3.5 / DeepSeek-V4.1-Flash, unknown → fallback warning
- [x] QA: `python3 -m pytest tests/ -q` green (существующие тесты не сломаны)
- [x] QA: `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` == 0
- [x] QA: live-прогон `sync_cloudru_prices.py` пишет кэш с ожидаемыми ставками
