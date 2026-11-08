# harness-bench-fast Domain Model

## Shot List
Subset of the 391-task benchmark selected for fast iteration. Preserves
 discriminative power while reducing runtime. v1 = 52 tasks (~13%).
Opposite of "full run" (--all).

## Discrimination Power
How well a task separates capable from incapable model/harness combos.
Measured as pass rate across 12 published runs. A task ALL 12 pass has
~0 discrimination. A task where 2/12 pass has maximum discrimination.

## Wave
A group of tasks testing a capability category. 391 tasks across 13 waves
in task-set v0.16.0:
- core (1-30), refactor (31-60), env_json (61-100)
- csv_xlsx (101-150), pipeline (151-205), diagnostic (206-221)
- memory (222-253), agentic (254-298), vcs (299-313)
- skills (314-330), adversarial (331-351), tbench (352-371)
- cli (372-391)

## Task Classification (by pass rate across 12 runs)
- Universal PASS (100%): 34 tasks — zero discrimination, smoke test only
- Low discrim (90-99%): 89 tasks — rare failures, regression watch
- Mid discrim (50-89%): 250 tasks — bulk of discrimination
- High discrim (<50%): 18 tasks — most informative per minute

## Stable Failure
task_378_cli_cfgctl_layered_merge — 2/12 pass (17%). Ceiling marker
for current agent capability. Bespoke CLI cfgctl is not understood.

## Coverage vs Speed Trade-off
Full 391-task run: ~15-35 min, high confidence. Shot list: ~4-7 min,
sufficient for regression testing and model comparison. 7-10x speedup.

## Cost-bounded capability sample
A stratified subset of the Medium waves run cheaply as a representative slice.
Currently 25% of 80 tasks (392–471) = 20 tasks; spans ceiling + floor anchors.
Distinct from the Light "Shot List" (which is v0.16.0, tasks 1–391).

## Task band (by published outcomes)
- **Ceiling** — passed by every available configuration (3/3). Capability proof / wiring.
- **Boundary** — passed by some (1–2/3). Most discriminative.
- **Floor** — passed by none (0/3). Capability limit.
Bands are read "by available configs" only (docs/<model>-medium90-*.json: codex,
miniswe, claudecode); a different config set can move a task between bands.

## Cost-weighted stratification
Allocating the sample quota across waves by **cost**, not wave size: the expensive
long wave gets a smaller share so the floor anchors do not inflate spend.

## Umbrella suite "Medium (392–471)"
One suite covering long 20 + reflection 20 + feasibility 40, so the fork table keeps
a single denominator. Registered in `scripts/build_fork_results.py`.

## Step cap (graph supersteps)
A hard limit on LangGraph supersteps (model + tool nodes), via `recursion_limit`;
0 = unlimited. Native to the deepagents runner, **not yet wired into the Pi
runner**. Acts as a runaway guard, not proportional savings.

## Sanitary timeout
Wall-clock per-task guard (`--timeout`; `DEFAULT_TASK_TIMEOUT_SECONDS = 3600`).
Kills the container on expiry; a coarse cost proxy. A task's `min_timeout_seconds`
can raise the effective value.

## Partial measurement
A wave measured on fewer tasks than its full size; recorded as
`measurement: "partial"` and never rendered as 0/N.

## Wilson interval
95% score interval for a binomial proportion (z = 1.96), computed per wave. It
describes **task outcomes**, not repeat variability (k = 1).

## Fork layer
Fork-authored documentation layered over upstream: the `FORK.md` index, the
`docs/fork*.{html,md}` pages, the README banner, and the generated result tables.
Kept out of upstream files so merges do not conflict (fork-doc-layering skill).

## Generator
A script that reads run JSON envelopes and rewrites one fork artifact — either the
guarded auto-block or the unified HTML page and its per-suite JSON. Three exist:
`scripts/build_fork_pages.py`, `scripts/build_fork_home.py`,
`scripts/build_fork_results.py`.

## Suite registration
Adding a run wave's filename pattern to a generator's include regex plus a display
name, sort order, and harness/model classifier branches. An unregistered stem is
silently skipped — the main "published nothing" bug class.

## Classifier (stem -> metadata)
The mapping from a run filename stem to `(harness, model, reasoning level)`
(`HARNESS_PREFIXES`, `MODEL_TOKENS`, `THINKING_LEVEL_RE`). Currently duplicated per
generator; a token added to one leaves the others rendering blank.

## Detail page
A per-run HTML page (`docs/fork-detail-<stem>.html`, EN mirror `.en`) listing the
run's waves, per-task rows, and source files; a table row links to it via
`details_url` / `data-detail`.

## Publish
The step that turns finished `results/*.json` into committed fork docs and a
deployed GitHub Pages site. Distinct from a benchmark **run**; not yet wired to run
completion (there is no run -> publish hook).

## Coverage / sample manifest
A truncated subset view (Light shot list, Medium sample/pilot) rendered from a
manifest of task ids, not from every scanner-matched run file.

## Relationships
- Shot List = smoke(5) + high-discrim(18) + mid-discrim(25) + low-discrim(4)
- Publish = generators (per artifact) + checks (--check/--lint on RU+EN) + Pages deploy
- Classifier feeds every suite row's Harness/Model/Profile cells; Suite registration gates whether a run reaches the table at all
- Wave coverage: all 13 waves have >= 2 tasks in shot list
- Discrimination Power determines shot list membership
- Capability sample = cost-weighted slice of the Medium waves, stratified by Task band
- Umbrella suite gives the capability sample a single denominator
