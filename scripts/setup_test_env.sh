#!/usr/bin/env bash
# setup_test_env.sh — provision the test/dev environment for harness-bench-fast.
#
# Goal: a reproducible, idempotent way to install the project (editable) plus the
# dev/test extras so that `pytest tests/` COLLECTS WITH 0 ERRORS.
#
# Three repo tests need deps that a bare `pip install -e .` does not provide:
#   tests/test_chat_openai.py    -> openai            (via langchain-openai)
#   tests/test_rli_backend.py    -> deepagents        (base dep; pulls langgraph)
#   tests/test_runner_policy.py  -> langgraph
# Installing `-e '.[openrouter]'` (langchain-openai==1.2.2) + base deepagents
# covers all three transitively.
#
# Usage:  scripts/setup_test_env.sh
# Env:    VENV=.venv  EXTRA=openrouter  (override as needed)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${VENV:-.venv}"
EXTRA="${EXTRA:-openrouter}"
PY="${VENV}/bin/python"

log() { printf '[setup_test_env] %s\n' "$*"; }

# --- pick installer (uv preferred, pip fallback) -----------------------------
if command -v uv >/dev/null 2>&1; then
  HAVE_UV=1
else
  log "uv not found in PATH — falling back to python -m venv + pip"
  HAVE_UV=0
fi

# --- 1. create the isolated venv ---------------------------------------------
if [ ! -x "$PY" ]; then
  if [ "$HAVE_UV" = 1 ]; then
    log "creating venv with uv: $VENV"
    uv venv "$VENV"
  else
    log "creating venv with python3 -m venv: $VENV"
    python3 -m venv "$VENV"
  fi
else
  log "reusing existing venv: $VENV"
fi

# --- 2. install project + test extras ----------------------------------------
install_pkgs() {
  if [ "$HAVE_UV" = 1 ]; then
    uv pip install --python "$PY" "$@"
  else
    "$PY" -m pip install "$@"
  fi
}

log "installing editable project with extras: -e .[${EXTRA}]"
install_pkgs -e ".[${EXTRA}]"

# --- 3. post-check imports; install pinned fallbacks if anything is missing ---
imports_missing() {
  # exit 0 if all present, exit 1 if any of the three is missing
  "$PY" - <<'PY'
import importlib.util
import sys

required = ("openai", "deepagents", "langgraph")
missing = [m for m in required if importlib.util.find_spec(m) is None]
if missing:
    sys.stderr.write("missing: " + ", ".join(missing) + "\n")
    sys.exit(1)
PY
}

if ! imports_missing; then
  log "some test deps still missing after base install — installing pinned fallbacks"
  install_pkgs "langchain-openai==1.2.2" "langgraph"
fi

# --- 4. hard verification (fail loudly) --------------------------------------
log "verifying test dependencies import cleanly"
"$PY" -c "import openai, deepagents, langgraph; print('deps ok')"

log "done. Run the suite with: $PY -m pytest tests/"
