"""Tests for config subcommands."""

from __future__ import annotations

import json

from cli_conformity import create_app
from cli_conformity.app import app_config
from cli_conformity.testing import invoke


def test_config_set_and_get(tmp_path):
    app = create_app(name="test-tool", env_prefix="TEST")
    app_config.config_dir = tmp_path

    result = invoke(app, ["config", "set", "server", "http://localhost:9000"])
    assert result.exit_code == 0

    result = invoke(app, ["config", "get", "server"])
    assert result.exit_code == 0
    assert "server" in result.output


def test_config_show(tmp_path):
    app = create_app(name="test-tool", env_prefix="TEST")
    app_config.config_dir = tmp_path

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"server": "http://example.com"}))

    result = invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "server" in result.output


def test_config_path(tmp_path):
    app = create_app(name="test-tool", env_prefix="TEST")
    app_config.config_dir = tmp_path

    result = invoke(app, ["config", "path"])
    assert result.exit_code == 0
    assert "path" in result.output


def test_config_known_keys(tmp_path):
    app = create_app(
        name="test-tool",
        env_prefix="TEST",
        known_config_keys={
            "server-url": "server_url",
            "server_url": "server_url",
        },
    )
    app_config.config_dir = tmp_path

    result = invoke(app, ["config", "set", "server-url", "http://example.com"])
    assert result.exit_code == 0

    config_file = tmp_path / "config.json"
    data = json.loads(config_file.read_text())
    assert data["server_url"] == "http://example.com"
