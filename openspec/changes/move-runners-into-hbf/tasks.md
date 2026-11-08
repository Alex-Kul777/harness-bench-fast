# Tasks: move-runners-into-hbf

## Implementation

- [x] Create feat/move-runners-into-hbf branch from origin/main
- [x] Write OpenSpec change (proposal.md, design.md, tasks.md)
- [ ] Write spec delta for benchmark-runs (MODIFIED)
- [x] Copy runners into HBF root (run_pi_bench.py, run_openclaw_bench.py, run_hermes_bench.py)
- [x] Fix BENCH_DIR path in each runner to point to self-directory
- [x] Add FORK-OWNED header to each runner
- [x] Create results/ directory in HBF with .gitkeep
- [x] Copy tests/test_runner_*.py into HBF tests/
- [x] Fix test imports to work from HBF root

## Documentation

- [x] Create RUNNERS_DEPRECATED.md in openclaw-workspace as deprecation pointer
- [x] Update harness-bench-fast skill run commands
- [x] Update HBF AGENTS.md if it references old paths

## QA / Verification

- [ ] openspec validate --all --strict exits 0
- [ ] Runner tests green from HBF: pytest tests/test_runner_*.py
- [ ] Smoke check: python3 run_pi_bench.py --help works from HBF
- [ ] git status clean on feat branch
