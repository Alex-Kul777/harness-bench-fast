# ADR-0002: OpenSpec vs the mattpocock engineering flow

Date: 2026-11-05
Status: accepted
Context: Two process layers now exist in this repo. OpenSpec (spec-driven,
`openspec/`) owns behavioural change: deltas under `openspec/changes/<id>/`,
`validate --strict` in CI, archive into `openspec/specs/`. Separately, the
`mattpocock/skills` suite is installed globally (`~/.openclaw/shared-skills/`)
and offers a main flow `grill-with-docs → to-spec → to-tickets → implement →
code-review → retro`, driven by an issue tracker. Running both as the primary
process would double-book the spec and the ticket graph.

Decision: **OpenSpec is the source of truth for behavioural change in this repo.
The engineering flow supplies the thinking shell around it.**

- Refining an idea / domain language → `grilling`, `grill-with-docs`,
  `domain-modeling` (produce/refresh `GLOSSARY.md`, ADRs).
- The agreed idea becomes an OpenSpec `change`, not a `to-spec` spec.
- `to-tickets` is used only for genuinely multi-session efforts, and its tickets
  reference `openspec/changes/<id>`.
- Building → `implement` (drives `tdd`) with `code-review-two-axis`/`solo-review`.
- Long or uncertain investigations → `research` (background agent, cited file).
- Hard bugs → `diagnosing-bugs`; closing reflection → `retro`.

Consequences:
- (+) One spec bookkeeping (OpenSpec) and one CI gate.
- (+) The flow's thinking stages (grilling, research, diagnosis, review, retro)
  are available without competing for spec ownership.
- (-) Two vocabularies to keep aligned; `GLOSSARY.md` stays the single source.
- (risk) Contributors may reach for `to-spec` out of habit; the `## Agent skills`
  block in `AGENTS.md` and this ADR are the pointer back.
