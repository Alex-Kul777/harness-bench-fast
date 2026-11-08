#!/usr/bin/env python3
# FORK-OWNED: not in upstream ai-forever/harness-bench-fast
"""Hermes Benchmark Runner — runs harness-bench-fast tasks through Hermes agent.

Uses `hermes chat -q` to run each task in an isolated session with
clean config (--ignore-rules --yolo -Q). Verifies with harness-bench-fast verifiers.

Usage:
    python run_hermes_bench.py --pilot           # 12 tasks (6 failed + 6 passed)
    python run_hermes_bench.py --failed-only      # 6 failed tasks
    python run_hermes_bench.py --tasks task_01_create_hello
    python run_hermes_bench.py --all               # all 391 tasks
    python run_hermes_bench.py --shot-list         # 52-task stratified sample
    python run_hermes_bench.py --all --concurrency 3 --json-output results/hermes_full_391.json
    python run_hermes_bench.py --all --rerun-on-fail  # resume, re-run failed only
    python run_hermes_bench.py --shot-list --thinking-off  # shot list, reasoning disabled
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tempfile import TemporaryDirectory

# Default to the local harness-bench-fast checkout.
_DEFAULT_BENCH_DIR = str(Path(__file__).parent)
BENCH_DIR = Path(os.environ.get("BENCH_DIR", _DEFAULT_BENCH_DIR))
sys.path.insert(0, str(BENCH_DIR))

SHOT_LIST_FILE = BENCH_DIR / "shot_list.txt"

from harness_bench.tasks import ALL_TASKS, get_task

DEFAULT_MODEL = "zai-org/GLM-5.2"
DEFAULT_TIMEOUT = 660
DEFAULT_CONCURRENCY = 3
HERMES_BIN = os.environ.get("HERMES_BIN", "hermes")

# Cloud.ru Foundation Models API — provider config for --ignore-user-config mode.
CLOUD_RU_BASE_URL = "https://foundation-models.api.cloud.ru/v1/"
CLOUD_RU_API_KEY = os.environ.get("CLOUD_RU_API_KEY", "")

# Load API key from Hermes .env if not set in environment
if not CLOUD_RU_API_KEY:
    _hermes_env = Path.home() / ".hermes" / ".env"
    if _hermes_env.exists():
        for line in _hermes_env.read_text().splitlines():
            if line.startswith("CLOUD_RU_KAP_HERMES="):
                CLOUD_RU_API_KEY = line.split("=", 1)[1].strip()
                break
    if not CLOUD_RU_API_KEY:
        print("WARNING: CLOUD_RU_API_KEY not found. Set it or ensure ~/.hermes/.env has CLOUD_RU_KAP_HERMES", file=sys.stderr)

# Memory tasks (222-253) ship AGENTS.md fixture with instructions to read/write MEMORY.md.
# --ignore-rules would skip AGENTS.md → all memory tasks FAIL.
# Hybrid approach: memory tasks run WITHOUT --ignore-rules, all others WITH it.
_MEMORY_TASK_PREFIXES = tuple(f"task_{n}_" for n in range(222, 254))


def _is_memory_task(task_id: str) -> bool:
    """Check if task is a memory task (222-253) that needs AGENTS.md."""
    return task_id.startswith(_MEMORY_TASK_PREFIXES)

FAILED_TASK_IDS = [
    "task_223_memory_city_timezone_script",
    "task_293_tau2_event_ticket_exchange",
    "task_355_segment_audit",
    "task_376_cli_xtab_column_share",
    "task_378_cli_cfgctl_layered_merge",
    "task_389_cli_find_xargs_predicates",
]

PASSED_TASK_IDS = [
    "task_01_create_hello",
    "task_13_count_csv_lines",
    "task_50_fix_typo",
    "task_76_create_dataclass",
    "task_100_zero_balance",
    "task_200_impl_priority_queue",
]

PILOT_TASK_IDS = FAILED_TASK_IDS + PASSED_TASK_IDS

# Thread lock for checkpoint writes
_write_lock = threading.Lock()

# Pricing for cost estimation (Cloud.ru, GLM-5.2, August 2026)
PRICE_INPUT_PER_M = 239.12   # ₽ per 1M input tokens
PRICE_OUTPUT_PER_M = 751.52  # ₽ per 1M output tokens


def run_one_task(task, *, model=DEFAULT_MODEL, timeout=DEFAULT_TIMEOUT, keep_workspace=False, thinking_off=False):
    """Run a single benchmark task through `hermes chat -q`."""
    started = time.monotonic()
    workspace_keepalive = None

    try:
        if keep_workspace:
            workspace_path = Path(f"/tmp/hermes_bench_{task.id}")
            # Вариант 2: очистка workspace перед каждой задачей — предотвращает contamination
            shutil.rmtree(workspace_path, ignore_errors=True)
            workspace_path.mkdir(parents=True, exist_ok=True)
        else:
            workspace_keepalive = TemporaryDirectory(prefix=f"hermes_bench_{task.id}_")
            workspace_path = Path(workspace_keepalive.name)

        # 1. Setup workspace with task fixtures
        task.setup(workspace_path)

        # 2. Build hermes command
        # --ignore-user-config: no user plugins/MCP/credentials (ALL tasks)
        # --ignore-rules: no AGENTS.md/SOUL.md/memory injection — ONLY for non-memory tasks
        # --yolo: auto-approve all tool calls
        # -Q: quiet mode (programmatic use)
        # -v: verbose — needed for token stats parsing
        # --max-turns 120: limit agent loop iterations
        # --source tool: mark sessions as tool-origin
        # --provider custom: use OPENAI_API_KEY/OPENAI_BASE_URL env vars (Cloud.ru)
        #
        # NOTE: --ignore-user-config skips config.yaml entirely, so
        # agent.reasoning_effort=none would be ignored. When thinking_off
        # is set, we skip --ignore-user-config and rely on the config.yaml
        # having reasoning_effort=none set by the caller.
        cmd = [
            HERMES_BIN, "chat",
            "-q", task.prompt,
            "--model", model,
            "--provider", "custom",
            "--yolo",
            "-Q",
            "-v",
            "--max-turns", "120",
            "--source", "tool",
        ]

        # --ignore-user-config only when NOT thinking-off (so config.yaml is read)
        if not thinking_off:
            cmd.append("--ignore-user-config")

        # Hybrid: only non-memory tasks get --ignore-rules
        if not _is_memory_task(task.id):
            cmd.append("--ignore-rules")

        # 3. Run hermes with cwd=workspace
        agent_error = None
        session_id = None
        try:
            run_env = os.environ.copy()
            run_env["OPENAI_API_KEY"] = CLOUD_RU_API_KEY
            run_env["OPENAI_BASE_URL"] = CLOUD_RU_BASE_URL

            result = subprocess.run(
                cmd,
                cwd=str(workspace_path),
                capture_output=True,
                text=True,
                timeout=timeout + 60,
                encoding="utf-8",
                errors="replace",
                env=run_env,
            )
            if result.returncode != 0:
                stderr_tail = (result.stderr or "")[-300:]
                agent_error = f"exit={result.returncode}: {stderr_tail}"

            # Extract session_id and token stats from verbose output
            combined_output = (result.stdout or "") + (result.stderr or "")
            if combined_output:
                m = re.search(r"session_id:\s+(\S+)", combined_output)
                if m:
                    session_id = m.group(1)

        except subprocess.TimeoutExpired:
            agent_error = f"timed out after {timeout}s"
            result = None
        except Exception as exc:
            agent_error = f"exception: {exc}"
            result = None

        elapsed = time.monotonic() - started

        # 4. Verify the result
        verify_result = task.verify(workspace_path)

        # 5. Extract token stats from verbose output
        # Hermes -v outputs lines like:
        #   "Token usage: prompt=19,945, completion=20, total=19,965"
        # One per API call — sum all calls for total task tokens.
        token_stats = {}
        if result and result.stderr:
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            for m in re.finditer(r"Token usage:\s+prompt=([\d,]+),\s+completion=([\d,]+),\s+total=([\d,]+)", result.stderr):
                input_tokens += int(m.group(1).replace(",", ""))
                output_tokens += int(m.group(2).replace(",", ""))
                total_tokens += int(m.group(3).replace(",", ""))
            if total_tokens > 0:
                token_stats = {
                    "agent_input_tokens": input_tokens,
                    "agent_output_tokens": output_tokens,
                    "agent_total_tokens": total_tokens,
                }

        # 6. Extract step count from verbose output
        # Hermes -v outputs tool call info; count tool_call markers.
        # Also try to get api_call_count from verbose output.
        if result and result.stderr:
            tool_calls = len(re.findall(r"Tool call:\s+\w+", result.stderr))
            api_calls = len(re.findall(r"Token usage:", result.stderr))
            if tool_calls > 0:
                token_stats["agent_tool_calls"] = tool_calls
            if api_calls > 0:
                token_stats["agent_api_calls"] = api_calls
            # Steps = agent turns (API calls), consistent with harness-bench definition
            token_stats["agent_steps"] = api_calls if api_calls > 0 else None

        return {
            "task_id": task.id,
            "passed": verify_result.passed,
            "message": verify_result.message,
            "elapsed_seconds": round(elapsed, 2),
            "error": agent_error,
            "workspace": str(workspace_path) if keep_workspace else None,
            "session_id": session_id,
            **token_stats,
        }

    except Exception as exc:
        elapsed = time.monotonic() - started
        return {
            "task_id": task.id,
            "passed": False,
            "message": f"runner error: {exc}",
            "elapsed_seconds": round(elapsed, 2),
            "error": str(exc),
            "workspace": None,
        }
    finally:
        if workspace_keepalive is not None and not keep_workspace:
            workspace_keepalive.cleanup()


def _write_results(results, path):
    """Write results JSON with summary. Thread-safe."""
    with _write_lock:
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        total_seconds = round(sum(r["elapsed_seconds"] for r in results), 1)
        total_in = sum(r.get("agent_input_tokens", 0) for r in results)
        total_out = sum(r.get("agent_output_tokens", 0) for r in results)
        total_tok = sum(r.get("agent_total_tokens", 0) for r in results)
        total_steps = sum(r.get("agent_steps", 0) or 0 for r in results)
        cost_rub = round(total_in / 1e6 * PRICE_INPUT_PER_M + total_out / 1e6 * PRICE_OUTPUT_PER_M, 2)
        payload = {
            "results": results,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": round(passed / max(total, 1), 4),
                "total_seconds": total_seconds,
                "total_input_tokens": total_in,
                "total_output_tokens": total_out,
                "total_tokens": total_tok,
                "total_steps": total_steps,
                "estimated_cost_rub": cost_rub,
            },
        }
        tmp_path = str(path) + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)


def _write_status(path, completed, total_task_count, results, started_at):
    """Write status file for progress monitoring. Thread-safe."""
    with _write_lock:
        passed = sum(1 for r in results if r["passed"])
        failed = sum(1 for r in results if not r["passed"])
        elapsed = time.monotonic() - started_at
        remaining = (elapsed / max(completed, 1)) * (total_task_count - completed) if completed > 0 else 0
        total_in = sum(r.get("agent_input_tokens", 0) for r in results)
        total_out = sum(r.get("agent_output_tokens", 0) for r in results)
        total_tok = total_in + total_out
        cost_rub = round(total_in / 1e6 * PRICE_INPUT_PER_M + total_out / 1e6 * PRICE_OUTPUT_PER_M, 2)
        last_task = results[-1]["task_id"] if results else None
        status = {
            "completed": completed,
            "total": total_task_count,
            "passed": passed,
            "failed": failed,
            "elapsed_seconds": round(elapsed, 1),
            "estimated_remaining_seconds": round(remaining, 1),
            "total_tokens": total_tok,
            "estimated_cost_rub": cost_rub,
            "last_task": last_task,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)


def _load_checkpoint(json_path):
    """Load existing results from checkpoint file for resume."""
    if not json_path or not Path(json_path).exists():
        return {}
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        return {r["task_id"]: r for r in data.get("results", [])}
    except (json.JSONDecodeError, KeyError):
        return {}


def run_batch(task_ids, *, model=DEFAULT_MODEL, timeout=DEFAULT_TIMEOUT,
               keep_workspace=False, json_output=None, concurrency=1,
               status_file=None, rerun_on_fail=False, fresh=False,
               thinking_off=False):
    """Run tasks with optional concurrency, checkpoint/resume, and progress reporting."""

    # Checkpoint/resume: load existing results
    existing_results = {}
    if json_output and not fresh:
        existing_results = _load_checkpoint(json_output)
        if existing_results:
            if rerun_on_fail:
                # Keep passed tasks, re-run failed ones
                skipped = [tid for tid in task_ids if tid in existing_results and existing_results[tid]["passed"]]
                pending = [tid for tid in task_ids if tid not in skipped]
                print(f"Checkpoint: {len(skipped)} passed tasks skipped, {len(pending)} to run", flush=True)
            else:
                # Skip all tasks in checkpoint
                skipped = [tid for tid in task_ids if tid in existing_results]
                pending = [tid for tid in task_ids if tid not in existing_results]
                print(f"Resume: {len(skipped)} tasks completed, {len(pending)} remaining", flush=True)
        else:
            pending = list(task_ids)
    else:
        pending = list(task_ids)

    # Start with existing passed results (for rerun_on_fail) or empty
    if rerun_on_fail and existing_results:
        results = [existing_results[tid] for tid in task_ids if tid in existing_results and existing_results[tid]["passed"]]
    elif not fresh and existing_results:
        results = [existing_results[tid] for tid in task_ids if tid in existing_results]
    else:
        results = []

    total_all = len(task_ids)
    started_at = time.monotonic()
    completed = len(results)

    if not pending:
        print("Nothing to run — all tasks already in checkpoint.", flush=True)
        return results

    print(f"Running {len(pending)} tasks (concurrency={concurrency})", flush=True)

    if concurrency <= 1:
        # Sequential mode (for debugging)
        for tid in pending:
            task = get_task(tid)
            print(f"[{completed+1}/{total_all}] {task.id}", flush=True)
            run = run_one_task(task, model=model, timeout=timeout, keep_workspace=keep_workspace, thinking_off=thinking_off)
            results.append(run)
            completed += 1
            status = "PASS" if run["passed"] else "FAIL"
            print(f"  [{status}] {run['elapsed_seconds']:.1f}s — {run['message'][:120]}", flush=True)
            if json_output:
                _write_results(results, json_output)
            if status_file:
                _write_status(status_file, completed, total_all, results, started_at)
    else:
        # Parallel mode with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            future_to_task = {}
            for tid in pending:
                task = get_task(tid)
                future = pool.submit(run_one_task, task, model=model, timeout=timeout, keep_workspace=keep_workspace, thinking_off=thinking_off)
                future_to_task[future] = tid

            for future in as_completed(future_to_task):
                tid = future_to_task[future]
                run = future.result()
                results.append(run)
                completed += 1
                status = "PASS" if run["passed"] else "FAIL"
                print(f"[{completed}/{total_all}] {tid}: [{status}] {run['elapsed_seconds']:.1f}s — {run['message'][:120]}", flush=True)
                if json_output:
                    _write_results(results, json_output)
                if status_file:
                    _write_status(status_file, completed, total_all, results, started_at)

    # Sort results by task_id for consistent output
    results.sort(key=lambda r: r["task_id"])

    return results


def _load_shot_list():
    """Load task IDs from shot_list.txt."""
    if not SHOT_LIST_FILE.exists():
        print(f"ERROR: shot list not found at {SHOT_LIST_FILE}", file=sys.stderr)
        sys.exit(1)
    return [line.strip() for line in SHOT_LIST_FILE.read_text().splitlines() if line.strip() and not line.startswith("#")]


def _set_hermes_reasoning(value: str):
    """Set agent.reasoning_effort in hermes config."""
    subprocess.run(
        [HERMES_BIN, "config", "set", "agent.reasoning_effort", value, "--force"],
        capture_output=True, timeout=10,
    )


def main():
    parser = argparse.ArgumentParser(description="Run harness-bench-fast via Hermes")
    parser.add_argument("--tasks", nargs="+", help="Specific task IDs")
    parser.add_argument("--failed-only", action="store_true")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--shot-list", action="store_true", help="Run the 52-task shot list")
    parser.add_argument("--thinking-off", action="store_true", help="Disable model reasoning (sets agent.reasoning_effort=none)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--keep", action="store_true", help="Keep workspaces")
    parser.add_argument("--json-output", default=None)
    parser.add_argument("--status-file", default=None, help="Write progress status to this file")
    parser.add_argument("--rerun-on-fail", action="store_true", help="Resume: keep passed, re-run failed")
    parser.add_argument("--fresh", action="store_true", help="Ignore checkpoint, run from scratch")
    args = parser.parse_args()

    if args.tasks:
        task_ids = args.tasks
    elif args.failed_only:
        task_ids = FAILED_TASK_IDS
    elif args.pilot:
        task_ids = PILOT_TASK_IDS
    elif args.shot_list:
        task_ids = _load_shot_list()
    elif args.all:
        task_ids = [t.id for t in ALL_TASKS]
    else:
        parser.print_help()
        sys.exit(1)

    # Handle reasoning toggle
    _restore_reasoning = None
    if args.thinking_off:
        _restore_reasoning = "medium"  # default to restore
        _set_hermes_reasoning("none")
        print("Reasoning: OFF (agent.reasoning_effort=none)", flush=True)

    json_output = args.json_output or f"/tmp/hermes_bench_{int(time.time())}.json"
    status_file = args.status_file or "/tmp/hermes_bench_status.json"

    thinking_tag = "_thinking_off" if args.thinking_off else ""
    print(f"Hermes Benchmark Runner")
    print(f"  Model: {args.model}")
    print(f"  Thinking: {'OFF' if args.thinking_off else 'ON (default)'}")
    print(f"  Tasks: {len(task_ids)}")
    print(f"  Concurrency: {args.concurrency}")
    print(f"  Timeout: {args.timeout}s")
    print(f"  JSON: {json_output}")
    print(f"  Status: {status_file}")
    print()

    try:
        results = run_batch(
            task_ids, model=args.model, timeout=args.timeout,
            concurrency=args.concurrency, keep_workspace=args.keep,
            json_output=json_output, status_file=status_file,
            rerun_on_fail=args.rerun_on_fail, fresh=args.fresh,
            thinking_off=args.thinking_off,
        )
    finally:
        # Restore reasoning setting
        if _restore_reasoning:
            _set_hermes_reasoning(_restore_reasoning)
            print(f"Reasoning restored to: {_restore_reasoning}", flush=True)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    total_in = sum(r.get("agent_input_tokens", 0) for r in results)
    total_out = sum(r.get("agent_output_tokens", 0) for r in results)
    total_tok = total_in + total_out
    total_steps = sum(r.get("agent_steps", 0) or 0 for r in results)
    cost = round(total_in / 1e6 * PRICE_INPUT_PER_M + total_out / 1e6 * PRICE_OUTPUT_PER_M, 2)

    print()
    print("=" * 60)
    print(f"Results: {passed}/{total} passed ({passed/max(total,1):.1%})")
    print(f"Steps: {total_steps}")
    print(f"Tokens: {total_tok:,} (in: {total_in:,} / out: {total_out:,})")
    print(f"Cost: ~{cost:,.0f} ₽")
    print(f"JSON: {json_output}")

    failed = [r for r in results if not r["passed"]]
    if failed:
        print(f"\nFailed tasks ({len(failed)}):")
        for r in failed:
            print(f"  {r['task_id']}: {r['message'][:100]}")


if __name__ == "__main__":
    main()
