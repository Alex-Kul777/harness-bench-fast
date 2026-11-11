"""Regression tests for run_hermes_bench.py Hermes 0.23.x CLI compatibility.

Change: fix-hermes-cli-compat.

Hermes 0.23.1 rejects ``-v`` on the gateway/non-TTY path (``exit=2:
Unsupported gateway CLI options: --verbose``) and ``--ignore-user-config`` drops
the provider config, so the runner MUST pass the custom endpoint/credential
explicitly, request ``--format stream-json`` and read usage from that JSONL
envelope. The model id MUST be bare for ``--provider custom`` (the Cloud.ru
provider prefix makes the API return HTTP 404).

Run: python3 -m pytest tests/test_runner_hermes_stream_json.py -q
"""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RAW_PREFIXED = "custom-foundation-models-api-cloud-ru/deepseek-ai/DeepSeek-V4.1-Flash"
BARE = "deepseek-ai/DeepSeek-V4.1-Flash"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


import pytest  # noqa: E402


@pytest.fixture(scope="module")
def hermes():
    return _load("hermes_runner_under_test", "run_hermes_bench.py")


# Real capture: `hermes chat -q ... --format stream-json` on a trivial task.
_RESULT_EVENT = {
    "type": "result",
    "session_id": "2026-11-11T08-20-13-abc123",
    "exit_code": 0,
    "text": "Done.",
    "tokens": {"input": 16311, "output": 3, "total": 16314,
               "cache_read": 128, "cache_write": 0},
    "duration_ms": 4210,
    "timestamp": 1762845613000,
}
_INIT_EVENT = {
    "type": "system", "subtype": "init", "model": BARE,
    "session_id": "2026-11-11T08-20-13-abc123", "timestamp": 1762845000000,
}
_TEXT_EVENT = {"type": "text", "text": "Do", "timestamp": 1762845000100}
_TOOL_USE_EVENT = {"type": "tool_use", "name": "shell", "timestamp": 1762845000200}


def _stdout(*events) -> str:
    return "\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n"


# ---------------------------------------------------------------------------
# Command: supported Hermes 0.23 flags only
# ---------------------------------------------------------------------------

def _cmd(hermes, **kw):
    kw.setdefault("model", RAW_PREFIXED)
    kw.setdefault("api_key", "sk-test-key")
    kw.setdefault("base_url", "https://foundation-models.api.cloud.ru/v1/")
    return hermes.build_chat_command("do the task", **kw)


def test_command_has_no_verbose_flag(hermes):
    # `-v` is unsupported on the gateway/non-TTY path -> must be gone.
    assert "-v" not in _cmd(hermes)
    assert "--verbose" not in _cmd(hermes)


def test_command_requests_stream_json(hermes):
    cmd = _cmd(hermes)
    assert "--format" in cmd
    assert cmd[cmd.index("--format") + 1] == "stream-json"


def test_command_passes_custom_endpoint_and_credential(hermes):
    cmd = _cmd(hermes)
    assert "--provider" in cmd and cmd[cmd.index("--provider") + 1] == "custom"
    assert "--base-url" in cmd
    assert cmd[cmd.index("--base-url") + 1] == "https://foundation-models.api.cloud.ru/v1/"
    assert "--api-key" in cmd
    assert cmd[cmd.index("--api-key") + 1] == "sk-test-key"


def test_command_uses_bare_model_id_for_custom_provider(hermes):
    cmd = _cmd(hermes)
    assert cmd[cmd.index("--model") + 1] == BARE


def test_command_keeps_supported_flags(hermes):
    cmd = _cmd(hermes, thinking="high")
    assert "--ignore-user-config" in cmd
    assert "--yolo" in cmd
    assert "--max-turns" in cmd and cmd[cmd.index("--max-turns") + 1] == "120"
    assert "--source" in cmd and cmd[cmd.index("--source") + 1] == "tool"
    assert "--reasoning" in cmd and cmd[cmd.index("--reasoning") + 1] == "high"
    assert "--ignore-rules" in cmd  # non-memory task


def test_command_omits_ignore_rules_for_memory_tasks(hermes):
    assert "--ignore-rules" not in _cmd(hermes, is_memory=True)


def test_bare_model_id_strips_provider_prefix(hermes):
    assert hermes._bare_model_id(RAW_PREFIXED) == BARE
    # A bare id (no provider prefix) is left untouched.
    assert hermes._bare_model_id(BARE) == BARE
    assert hermes._bare_model_id("zai-org/GLM-5.2") == "zai-org/GLM-5.2"


# ---------------------------------------------------------------------------
# Parser: usage from the stream-json `result` envelope
# ---------------------------------------------------------------------------

def test_parser_reads_tokens_from_result_event(hermes):
    stats, session_id, err = hermes._parse_stream_json(
        _stdout(_INIT_EVENT, _TEXT_EVENT, _TOOL_USE_EVENT, _RESULT_EVENT)
    )
    assert err is None
    assert session_id == "2026-11-11T08-20-13-abc123"
    assert stats["agent_input_tokens"] == 16311
    assert stats["agent_output_tokens"] == 3
    assert stats["agent_total_tokens"] == 16314
    assert stats["agent_cache_read_tokens"] == 128
    assert stats["agent_cache_write_tokens"] == 0
    assert stats["agent_tool_calls"] == 1
    assert stats["agent_steps"] == 1


def test_parser_result_only(hermes):
    # A bare result line (no text/tool events) still yields tokens.
    stats, session_id, err = hermes._parse_stream_json(_stdout(_RESULT_EVENT))
    assert err is None
    assert session_id == "2026-11-11T08-20-13-abc123"
    assert stats["agent_input_tokens"] == 16311
    assert stats["agent_total_tokens"] == 16314


def test_parser_missing_result_falls_back_to_zero_and_reports_error(hermes):
    stats, session_id, err = hermes._parse_stream_json(_stdout(_INIT_EVENT, _TEXT_EVENT))
    assert err is not None and "result" in err
    assert stats.get("agent_input_tokens", 0) == 0
    assert stats.get("agent_total_tokens", 0) == 0


def test_parser_ignores_non_json_lines(hermes):
    noisy = "starting up\nnot json\n" + _stdout(_RESULT_EVENT)
    stats, _, err = hermes._parse_stream_json(noisy)
    assert err is None
    assert stats["agent_total_tokens"] == 16314


def test_parser_reports_result_error(hermes):
    result = dict(_RESULT_EVENT)
    result["error"] = "Worker execution is unknown"
    stats, _, err = hermes._parse_stream_json(_stdout(result))
    assert err == "Worker execution is unknown"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
