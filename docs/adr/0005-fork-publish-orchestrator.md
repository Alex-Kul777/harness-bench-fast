# ADR-0005: Publish as one command, wired to run completion

Date: 2026-11-08
Status: accepted
Context: Publishing fork results is a manual, multi-step procedure — three
generators, a stem→metadata classifier duplicated across all of them, RU+EN
regeneration, `--check`/`--lint` on a clean `git archive`, commit, then a Pages
deploy + poll. There is no run→publish hook: a run writes `results/*.json` and
stops. The owner expected publish to follow a finished benchmark immediately, and
finds the manual chain slow. The `fork-doc-layering` skill encodes the rules but
no single executable entry point exists, and classifier edits are easy to make in
one generator and forget in another (silent blank cells on the published page).

Decision:
- **One entry point** `scripts/publish_fork.py` (Q1) that runs the generators in
  order, RU+EN, then `--check` + `--lint` on a clean archive of the staged tree,
  then the Pages deploy/verify poll.
- **Single metadata source** `scripts/fork_metadata.py` (Q2) holding
  `MODEL_TOKENS`, `HARNESS_PREFIXES`, `THINKING_LEVEL_RE`, the
  stem→(harness, model, level) resolver and `collect_paths()`; all three
  generators and the orchestrator import it. The per-generator copies are removed.
- The orchestrator **encapsulates the concurrency guard** (Q5): detect a running
  `run_bench`, move newer sibling `../results/*.json` to `/tmp`, restore after.
- An **unresolvable harness/model stem is a hard failure** (exit 1) listing the
  offending stems (Q7).
- **Auto-run (Q3, owner override):** publish runs automatically after a benchmark
  run, rather than as a separate manual step.
- **Push by default (Q4, owner override):** the orchestrator commits and pushes by
  default. This **supersedes** the earlier "do not push until the owner asks"
  convention. Push target and gating are decided in round 2.
- **Auto-trigger mechanism (Q8):** the runners gain `--publish`, default **ON** —
  the orchestrator runs in the same process when a run finishes; no watcher daemon.
- **Push target and gate (Q9):** push targets the fork `main` and is **fail-closed**
  — it happens only after `--check`/`--lint` pass on a clean archive; otherwise the
  orchestrator aborts and leaves the commit on the branch.
- **Opt-out flags (Q10):** `--no-publish`, `--no-commit`, `--no-push`, `--dry-run`
  are kept (defaults ON, explicit opt-out).
- **Incomplete-run guard (Q11):** the orchestrator hard-fails on a run whose JSON
  lacks a top-level `summary` or carries in-flight markers — a partial run is never
  published as a full-suite row.
- **Process (Q6):** implementation goes through an OpenSpec change on branch
  `fix/fork-run-steps`; `main` is untouched until the owner accepts.

Consequences:
  (+) One command; the classifier is edited once.
  (+) A run whose stem is unregistered fails loudly instead of silently skipping.
  (+) The published site updates immediately after a run.
  (-) Auto-push raises the blast radius: a bad classifier now ships without a
      human gate — mitigated by fail-closed `--check`/`--lint` before push.
  (risk) Auto-publish must never fire on a half-finished or partial run.

Refs: `GLOSSARY.md` (Fork layer, Generator, Suite registration, Classifier,
Detail page, Publish), `fork-doc-layering` skill, `scripts/build_fork_pages.py`,
`scripts/build_fork_home.py`, `scripts/build_fork_results.py`.
