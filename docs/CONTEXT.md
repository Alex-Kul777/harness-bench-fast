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

## Relationships
- Shot List = smoke(5) + high-discrim(18) + mid-discrim(25) + low-discrim(4)
- Wave coverage: all 13 waves have >= 2 tasks in shot list
- Discrimination Power determines shot list membership
- Refresh at task-set version bumps
