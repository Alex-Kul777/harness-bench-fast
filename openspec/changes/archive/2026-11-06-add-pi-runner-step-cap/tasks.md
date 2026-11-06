# add-pi-runner-step-cap — tasks

## 1. Feasibility (do first)

- [x] 1.1 Determine whether `pi-agent` accepts a step / recursion / max-steps limit — result: **ABSENT** (no flag, no dist code path, no env fallback). Evidence in `design.md`.

## 2. Реализация

- [x] 2.1 ~~Add `--recursion-limit` + `HBF_TASK_RECURSION_LIMIT`~~ — **dropped** (decision a): no real control to wire; no emulation.
- [x] 2.2 ~~Pass the cap through to `pi-agent`~~ — **dropped** (nothing to pass).
- [x] 2.3 ~~Disclose a finite budget in the prompt~~ — **n/a** (no finite cap).
- [x] 2.4 ~~Record `recursion_limit` in the run JSON~~ — **n/a**.

## 3. QA / верификация

- [x] 3.1 No code change ⇒ current Pi runner command is unchanged by construction
- [x] 3.2 Feasibility evidence captured (help output, dist grep, env inventory) in `design.md`
- [x] 3.3 `npx -y @fission-ai/openspec@1.16.0 validate --all --strict` → 0

## 4. Документация

- [x] 4.1 ADR-0004 updated: final lever = timeout-only; step cap unavailable; future options noted
