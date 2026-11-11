"""Shared benchmark-credential resolution for the fork runners.

All benchmark runs (every model × every harness: Pi / OpenClaw / Hermes) MUST
bill to the **dedicated benchmark account**, kept separate from the production
agent budget. The canonical env var is ``CLOUD_RU_BENCH_API_KEY``.

Resolution order (first non-empty wins):

1. ``CLOUD_RU_BENCH_API_KEY`` — the dedicated benchmark key (preferred).
2. ``CLOUD_RU_KAP_HERMES`` — legacy dedicated-ish key (env, then ``~/.hermes/.env``).
3. ``CLOUD_RU_API_KEY`` — the production agent key (last-resort fallback).

When the dedicated key is present the production key is **never** used. The
chosen source is reported on stderr as a ``NOTE`` (so a run's provenance is
visible without leaking the secret) and returned so runners can record it in the
run artifact (``summary.bench_credential``).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

#: Canonical dedicated benchmark key (owner provisions this in secret/env).
BENCH_API_KEY_ENV = "CLOUD_RU_BENCH_API_KEY"
#: Legacy key that already holds a dedicated account (env, else Hermes .env).
HERMES_API_KEY_ENV = "CLOUD_RU_KAP_HERMES"
#: Production agent key — the bench must NOT use it while a bench key is set.
PRODUCTION_API_KEY_ENV = "CLOUD_RU_API_KEY"

HERMES_ENV_PATH = Path.home() / ".hermes" / ".env"

#: Returned when no source supplied a key.
NO_SOURCE = "none"


def _read_var_from_file(path: Path | str | None, var: str) -> str | None:
    """Return ``var`` from a dotenv-style file, or ``None`` (best-effort)."""
    path = Path(path) if path is not None else HERMES_ENV_PATH
    try:
        if not path.exists():
            return None
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].lstrip()
            if line.startswith(var + "="):
                value = line.split("=", 1)[1].strip()
                return value.strip().strip('"').strip("'") or None
    except OSError:
        return None
    return None


def resolve_bench_api_key(
    env: dict | None = None,
    *,
    hermes_env_path: Path | str | None = None,
    warn: bool = True,
) -> tuple[str, str]:
    """Resolve the benchmark API key with dedicated-account priority.

    Returns ``(key, source)`` where *source* is the env-var name that supplied
    the key (one of :data:`BENCH_API_KEY_ENV`, :data:`HERMES_API_KEY_ENV`,
    :data:`PRODUCTION_API_KEY_ENV`) or :data:`NO_SOURCE` when nothing was found.

    *env* defaults to ``os.environ``; *hermes_env_path* overrides the fallback
    dotenv path (used by tests). When *warn* is true a short ``NOTE`` describing
    the chosen source is written to stderr (never the key value).
    """
    env = os.environ if env is None else env

    value = (env.get(BENCH_API_KEY_ENV) or "").strip()
    if value:
        source = BENCH_API_KEY_ENV
    else:
        value = (env.get(HERMES_API_KEY_ENV) or "").strip()
        if not value:
            value = _read_var_from_file(hermes_env_path, HERMES_API_KEY_ENV) or ""
        if value:
            source = HERMES_API_KEY_ENV
        else:
            value = (env.get(PRODUCTION_API_KEY_ENV) or "").strip()
            source = PRODUCTION_API_KEY_ENV if value else NO_SOURCE

    if warn:
        if source == BENCH_API_KEY_ENV:
            print(
                f"NOTE: benchmark key resolved from dedicated {BENCH_API_KEY_ENV}",
                file=sys.stderr,
            )
        elif source == HERMES_API_KEY_ENV:
            print(
                f"NOTE: benchmark key resolved from {HERMES_API_KEY_ENV} "
                f"(dedicated {BENCH_API_KEY_ENV} not set)",
                file=sys.stderr,
            )
        elif source == PRODUCTION_API_KEY_ENV:
            print(
                f"NOTE: benchmark key falling back to production {PRODUCTION_API_KEY_ENV} "
                f"(set {BENCH_API_KEY_ENV} to isolate the bench budget)",
                file=sys.stderr,
            )
        else:
            print(
                "WARNING: benchmark key not found "
                f"(set {BENCH_API_KEY_ENV} or {HERMES_API_KEY_ENV})",
                file=sys.stderr,
            )

    return value or "", source
