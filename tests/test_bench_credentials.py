"""Regression tests for the dedicated benchmark-credential resolver.

Change: use-dedicated-bench-account.

Pins that ``harness_bench.bench_credentials.resolve_bench_api_key`` applies the
dedicated-account priority for every benchmark run (all models × harnesses):

    CLOUD_RU_BENCH_API_KEY -> CLOUD_RU_KAP_HERMES (env, then ~/.hermes/.env)
    -> production CLOUD_RU_API_KEY

and that the production key is never chosen while a dedicated bench key is set.
It also pins the stderr NOTE that records which source supplied the key.

Run: python3 -m pytest tests/test_bench_credentials.py -q
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness_bench.bench_credentials import (  # noqa: E402
    BENCH_API_KEY_ENV,
    HERMES_API_KEY_ENV,
    NO_SOURCE,
    PRODUCTION_API_KEY_ENV,
    resolve_bench_api_key,
)

BENCH = "bench-key-dedicated"
HERMES = "hermes-dedicated"
PROD = "production-agent-key"


def _resolve(env, tmp_path, capsys, hermes=None):
    result = resolve_bench_api_key(
        env, hermes_env_path=tmp_path / "hermes.env" if hermes is None else hermes
    )
    err = capsys.readouterr().err
    return result, err


def test_bench_key_has_top_priority(tmp_path, capsys):
    env = {
        BENCH_API_KEY_ENV: BENCH,
        HERMES_API_KEY_ENV: HERMES,
        PRODUCTION_API_KEY_ENV: PROD,
    }
    (key, source), err = _resolve(env, tmp_path, capsys)
    assert (key, source) == (BENCH, BENCH_API_KEY_ENV)
    assert "CLOUD_RU_BENCH_API_KEY" in err


def test_production_never_used_when_bench_key_set(tmp_path, capsys):
    # Even with the production key present, the dedicated key must win.
    env = {BENCH_API_KEY_ENV: BENCH, PRODUCTION_API_KEY_ENV: PROD}
    (key, source), _ = _resolve(env, tmp_path, capsys)
    assert key == BENCH
    assert key != PROD
    assert source == BENCH_API_KEY_ENV


def test_hermes_env_var_is_fallback(tmp_path, capsys):
    env = {HERMES_API_KEY_ENV: HERMES, PRODUCTION_API_KEY_ENV: PROD}
    (key, source), err = _resolve(env, tmp_path, capsys)
    assert (key, source) == (HERMES, HERMES_API_KEY_ENV)
    assert "CLOUD_RU_KAP_HERMES" in err


def test_hermes_dotenv_file_is_fallback(tmp_path, capsys):
    dotenv = tmp_path / "hermes.env"
    dotenv.write_text(f'# comment\nexport {HERMES_API_KEY_ENV}="{HERMES}"\n')
    env = {PRODUCTION_API_KEY_ENV: PROD}
    (key, source), _ = _resolve(env, tmp_path, capsys, hermes=dotenv)
    assert (key, source) == (HERMES, HERMES_API_KEY_ENV)


def test_production_is_last_resort(tmp_path, capsys):
    env = {PRODUCTION_API_KEY_ENV: PROD}
    (key, source), err = _resolve(env, tmp_path, capsys)
    assert (key, source) == (PROD, PRODUCTION_API_KEY_ENV)
    assert BENCH_API_KEY_ENV in err  # hint to isolate the bench budget


def test_no_key_found(tmp_path, capsys):
    (key, source), err = _resolve({}, tmp_path, capsys)
    assert (key, source) == ("", NO_SOURCE)
    assert "WARNING" in err


def test_note_is_distinguishable_per_source(tmp_path, capsys):
    notes = {}
    for env in (
        {BENCH_API_KEY_ENV: BENCH},
        {HERMES_API_KEY_ENV: HERMES},
        {PRODUCTION_API_KEY_ENV: PROD},
    ):
        _, err = _resolve(env, tmp_path, capsys)
        assert "key" not in err.replace("benchmark key", "")  # never leaks the value
        notes[err.strip()] = True
    # Each source produces its own recognisable note.
    assert len(notes) == 3


def test_empty_bench_key_falls_through(tmp_path, capsys):
    env = {BENCH_API_KEY_ENV: "   ", PRODUCTION_API_KEY_ENV: PROD}
    (key, source), _ = _resolve(env, tmp_path, capsys)
    assert (key, source) == (PROD, PRODUCTION_API_KEY_ENV)
