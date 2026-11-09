# Tasks: fix-test-env-provisioning

- [x] Написать `openspec/changes/fix-test-env-provisioning/{proposal,design,tasks}.md` + `specs/dev-environment/spec.md`
- [x] Добавить `scripts/setup_test_env.sh` (uv-based + pip fallback, `-e '.[openrouter]'`, post-check импортов, до-установка недостающих)
- [x] Сделать скрипт идемпотентным и исполняемым (`chmod +x`)
- [x] Добавить короткую заметку о провижинировании тест-окружения в `README.md` (если её нет)
- [x] Провижинировать изолированный `.venv` в этом worktree через `scripts/setup_test_env.sh`
- [x] QA: `.venv/bin/python -c "import openai, deepagents, langgraph; print('deps ok')"` → `deps ok`
- [x] QA: `.venv/bin/python -m pytest tests/ --collect-only -q` → **0 errors** (наблюдается `2025 tests collected`; ожидание задачи `1906` не совпадает с деревом)
- [x] QA: `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → exit 0
- [ ] (вне change) git commit/push/merge — не выполняется этим субагентом
