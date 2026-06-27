"""Tests for create_app() factory."""

from __future__ import annotations

from cli_conformity import create_app, output, state, sub_app_options, JsonOption, ProjectOption
from cli_conformity.testing import invoke

import typer


def test_default_flags_present():
    app = create_app(name="test-tool", env_prefix="TEST", description="A test tool.")
    result = invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--verbose" in result.output
    assert "--json" in result.output
    assert "--no-color" in result.output
    assert "--server" in result.output
    assert "--api-key" in result.output
    assert "--project" in result.output
    assert "--version" in result.output


def test_opt_out_server_flag():
    app = create_app(
        name="test-tool", env_prefix="TEST", server_flag=False,
    )
    result = invoke(app, ["--help"])
    assert "--server" not in result.output
    assert "--verbose" in result.output


def test_opt_out_project_flag():
    app = create_app(
        name="test-tool", env_prefix="TEST", project_flag=False,
    )
    result = invoke(app, ["--help"])
    assert "--project" not in result.output


def test_opt_out_api_key_flag():
    app = create_app(
        name="test-tool", env_prefix="TEST", api_key_flag=False,
    )
    result = invoke(app, ["--help"])
    assert "--api-key" not in result.output


def test_version_subcommand_registered():
    app = create_app(name="test-tool", env_prefix="TEST")
    result = invoke(app, ["version"])
    assert result.exit_code == 0
    assert "cli_version" in result.output


def test_version_flag():
    app = create_app(name="test-tool", env_prefix="TEST")
    result = invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "test-tool" in result.output


def test_config_subcommand_registered():
    app = create_app(name="test-tool", env_prefix="TEST")
    result = invoke(app, ["config", "--help"])
    assert result.exit_code == 0
    assert "show" in result.output
    assert "set" in result.output
    assert "get" in result.output
    assert "path" in result.output


def test_config_subcommand_opt_out():
    app = create_app(
        name="test-tool", env_prefix="TEST", global_config=False,
    )
    result = invoke(app, ["config", "--help"])
    assert result.exit_code != 0


def test_flags_populate_state():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def check():
        assert state.verbose is True
        assert state.json is True
        assert state.server == "http://example.com"

    result = invoke(app, ["--verbose", "--json", "--server", "http://example.com", "check"])
    assert result.exit_code == 0


def test_no_args_shows_help():
    app = create_app(name="test-tool", env_prefix="TEST", description="My tool.")
    result = invoke(app, [])
    assert "My tool." in result.output


def test_all_opt_outs():
    app = create_app(
        name="minimal",
        env_prefix="MIN",
        server_flag=False,
        api_key_flag=False,
        project_flag=False,
        global_config=False,
        guide=False,
        telemetry=False,
    )

    @app.command()
    def hello():
        output.success("hi")

    result = invoke(app, ["hello"])
    assert result.exit_code == 0


def test_env_var_populates_server():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def check():
        assert state.server == "http://from-env.com"

    result = invoke(app, ["check"], env={"TEST_SERVER": "http://from-env.com"})
    assert result.exit_code == 0


def test_sub_app_options_merges_project():
    app = create_app(name="test-tool", env_prefix="TEST")
    sub = typer.Typer(no_args_is_help=True)

    @sub.callback(invoke_without_command=True)
    def sub_cb(ctx: typer.Context, project: ProjectOption = None,
               json_output: JsonOption = False):
        sub_app_options(project=project, json_output=json_output)

    @sub.command()
    def show():
        assert state.project == "local-proj"
        assert state.json is True
        output.success("ok")

    app.add_typer(sub, name="sub", help="Sub app.")

    result = invoke(app, ["sub", "--project", "local-proj", "--json", "show"])
    assert result.exit_code == 0


def test_no_color_flag():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def check():
        assert state.no_color is True
        output.success("done")

    result = invoke(app, ["--no-color", "check"])
    assert result.exit_code == 0


def test_version_json_mode():
    app = create_app(name="test-tool", env_prefix="TEST")
    result = invoke(app, ["--json", "version"])
    assert result.exit_code == 0
    import json
    parsed = json.loads(result.output)
    assert "cli_version" in parsed
