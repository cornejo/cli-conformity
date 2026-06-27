"""Tests for output module — JSON vs Rich modes."""

from __future__ import annotations

import json

from cli_conformity import create_app, output
from cli_conformity.state import state
from cli_conformity.testing import invoke


def test_data_json_mode(capsys):
    state.json = True
    output.data({"key": "value"})
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed == {"key": "value"}


def test_data_text_mode(capsys):
    state.json = False
    output.data({"name": "alice"})
    captured = capsys.readouterr()
    assert "name:" in captured.out
    assert "alice" in captured.out


def test_success_json_mode(capsys):
    state.json = True
    output.success("done")
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["status"] == "ok"
    assert parsed["message"] == "done"


def test_error_json_mode(capsys):
    state.json = True
    output.error("fail", code="not_found")
    captured = capsys.readouterr()
    parsed = json.loads(captured.err)
    assert parsed["status"] == "error"
    assert parsed["code"] == "not_found"


def test_table_json_mode(capsys):
    state.json = True
    rows = [{"name": "a", "count": 1}, {"name": "b", "count": 2}]
    output.table(rows, ["name", "count"])
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "a"


def test_json_flag_via_cli():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def info():
        output.data({"hello": "world"})

    result = invoke(app, ["--json", "info"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert parsed == {"hello": "world"}


def test_format_age():
    assert output.format_age(None) == ""
    assert output.format_age("") == ""
    assert "ago" in output.format_age("2020-01-01T00:00:00Z")
