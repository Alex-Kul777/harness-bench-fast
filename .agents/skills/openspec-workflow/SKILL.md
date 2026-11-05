---
name: "openspec-workflow"
description: "Spec-driven workflow for this repo: explore/propose/apply/verify/archive using the OpenSpec CLI and openspec/ folder. Use for any behavior change in harness-bench-fast."
---

# OpenSpec workflow (harness-bench-fast)

Use this skill for any change to benchmark behavior, reporting or fork docs.
OpenSpec lives in `openspec/` (see `openspec/config.yaml`). The CLI is run via
`npx -y @fission-ai/openspec@1.16.0` (or a globally installed `openspec`).

## When to use
- New feature / behavior change / refactor in this repo
- Doc/table schema change (e.g. canonical result columns)
- Before spawning implementation subagents

## When NOT to use
- One-line typo fixes, pure data additions with no behavior change
- Reading/answering questions about the benchmark

## Lifecycle (maps to /opsx:* commands)
1. **explore** — map the problem; read specs in `openspec/specs/` first.
2. **propose** — create a change: `npx -y @fission-ai/openspec@1.16.0 new change <id>`
   → `openspec/changes/<id>/` with `proposal.md`, `specs/` (ADDED/MODIFIED/REMOVED),
   `design.md`, `tasks.md`. Get human review BEFORE coding.
3. **apply** — implement, ticking `tasks.md` only when behavior is fully done.
4. **verify** — run `npx -y @fission-ai/openspec@1.16.0 validate --all --strict`
   plus the repo's own checks (`python3 scripts/build_fork_results.py --check`).
5. **archive** — `openspec archive <id>` → folds deltas into `openspec/specs/`.

## Conventions (this repo)
- Spec prose may be Russian, but requirements MUST keep English `SHALL`, and
  scenarios MUST use `WHEN` / `THEN` (validator requirement).
- Source of truth: OpenSpec `specs/` = behavior; Workboard = execution;
  ADR/`design.md` = decisions. Upstream benchmark methodology stays in `README.md`.
- Fork-layer docs are merge-guarded (`<!-- FORK:BEGIN -->`, `FORK:RESULTS`).
- Create a Workboard card for changes taking >5 min; link its id in the proposal.

## Verification
- `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` exits 0.
- No change is archived while `tasks.md` has unchecked items.
