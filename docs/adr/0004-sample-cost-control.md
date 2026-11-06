# ADR-0004: Cost control for the capability sample

Date: 2026-11-06
Status: accepted
Context: ADR-0003 fixes the 25% capability sample but leaves the cost lever open.
A full Medium run is expensive (long ≈ 20M tokens and ≈ 2400 s per task; the long
pilot of 3 tasks cost ≈ 3265 ₽). Cost ≈ steps × average context, so the driver is
long, many-step tasks, and the lever must bound work, not just wall time.

Decision (amended 2026-11-06 after the feasibility check):
- **Final lever: sanitary `--timeout` only.** Per-wave values: long 2400,
  reflect 900, feasibility 1800. It is a coarse cost proxy that kills the container
  on expiry; a task's `min_timeout_seconds` can raise the effective value.
- **Step cap: not available, dropped.** The bundled agent in `pi-sandbox:latest`
  (`@earendil-works/pi-coding-agent` v1.5.0) exposes **no** step / recursion / turn
  limit — no flag, no dist code path, no env fallback (evidence in
  `openspec/changes/…` / `docs/adr` and the archived change). Wiring it would require
  emulation, which we reject. Target caps (long 600 / feasibility 150 / reflect 60)
  remain the desired values only if a future change provides a real mechanism.
- **Reuse.** The feasibility 12 already ran in `wave19_full_ds41flash.json` (36/40);
  reflect `412` and long `392` already have results. Only the missing tasks were
  re-run: reflect `422, 426, 415, 430` and long `403, 398`. This is itself the
  biggest single saving.

Consequences:
  (+) A working, deterministic *time* bound on runs today; reuse avoids re-spending.
  (-) No *work* bound: a slow long task is only cut by wall time, not by steps.
  (-) Sanitary timeout can produce false timeouts on legitimately slow long tasks.
  (future) External cap (monitor NDJSON, kill on threshold) or deepagents
  (`recursion_limit`) are the routes if a work bound is later required.

Refs: `GLOSSARY.md` (Sanitary timeout), ADR-0003, openspec change
`add-pi-runner-step-cap` (archived: limitation documented),
`harness_bench/runtime_limits.py`.
