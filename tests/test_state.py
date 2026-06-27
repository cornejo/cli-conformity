"""Tests for state and config resolution."""

from __future__ import annotations

import json
from pathlib import Path

from cli_conformity.state import (
    load_config,
    resolve_config,
    require_project,
    require_server,
    resolve_server,
    save_config,
    state,
)
from cli_conformity.errors import CliError

import pytest


def test_resolve_config_cli_wins(tmp_path, monkeypatch):
    state.env_prefix = "TEST"
    state.config_dir = tmp_path
    monkeypatch.setenv("TEST_SERVER", "from-env")
    save_config({"server": "from-file"})

    assert resolve_config("server", cli_value="from-cli") == "from-cli"


def test_resolve_config_env_wins(tmp_path, monkeypatch):
    state.env_prefix = "TEST"
    state.config_dir = tmp_path
    monkeypatch.setenv("TEST_SERVER", "from-env")
    save_config({"server": "from-file"})

    assert resolve_config("server") == "from-env"


def test_resolve_config_file_wins(tmp_path):
    state.env_prefix = "TEST"
    state.config_dir = tmp_path
    save_config({"server": "from-file"})

    assert resolve_config("server") == "from-file"


def test_resolve_config_default():
    state.env_prefix = "TEST"
    assert resolve_config("server", default="fallback") == "fallback"


def test_resolve_server_auto_prefixes_http():
    state.server = "myhost:8080"
    state.server_default = ""
    assert resolve_server() == "http://myhost:8080"


def test_resolve_server_preserves_https():
    state.server = "https://secure.example.com"
    assert resolve_server() == "https://secure.example.com"


def test_require_server_raises():
    state.server_default = ""
    state.server = None
    state.env_prefix = "TEST"
    with pytest.raises(CliError, match="No server specified"):
        require_server()


def test_require_project_explicit():
    assert require_project("my-project") == "my-project"


def test_require_project_from_state():
    state.project = "state-project"
    assert require_project() == "state-project"


def test_require_project_from_env(monkeypatch):
    state.env_prefix = "TEST"
    monkeypatch.setenv("TEST_PROJECT", "env-project")
    assert require_project() == "env-project"


def test_require_project_from_config(tmp_path):
    state.env_prefix = "TEST"
    state.config_dir = tmp_path
    state.name = "test-tool"
    save_config({"default_project": "config-project"})
    assert require_project() == "config-project"


def test_require_project_raises():
    state.env_prefix = "TEST"
    state.name = "test-tool"
    with pytest.raises(CliError, match="No project specified"):
        require_project()


def test_load_save_config(tmp_path):
    state.config_dir = tmp_path
    save_config({"key": "value"})
    assert load_config() == {"key": "value"}

    config_file = tmp_path / "config.json"
    assert config_file.exists()
    assert json.loads(config_file.read_text()) == {"key": "value"}


def test_load_config_missing():
    state.config_dir = Path("/nonexistent/path")
    assert load_config() == {}
