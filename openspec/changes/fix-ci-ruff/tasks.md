# Tasks: fix-ci-ruff

## Implementation

- [x] Run `uv run ruff check . --fix` (68 safe fixes)
- [x] Triage and fix the 27 remaining findings by rule (E402, F402, F821, F841, B007, B904, B905, E702, E741, SIM105, SIM109, SIM110)
- [x] Update `tests/test_fork_sample_columns.py` for the new leading `#` column (12 cols) so pytest passes once Ruff is green
- [x] Re-run `uv run ruff check .` → "All checks passed!"

## Spec / Docs

- [x] Write OpenSpec change (`proposal.md`, `design.md`, `tasks.md`, `specs/code-quality/spec.md`)

## QA / Verification

- [x] `uv run ruff check .` exits 0
- [x] `python3 scripts/build_fork_results.py --check`, `build_fork_pages.py --check`, `build_fork_home.py --check` all green
- [x] `uv run pytest -q` passes
- [ ] CI job "Quality" green on the PR before merge
