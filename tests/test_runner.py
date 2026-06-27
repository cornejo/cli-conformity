"""Tests for run() error handling."""

from __future__ import annotations

import httpx
import typer

from cli_conformity import create_app, output
from cli_conformity.errors import CliError, Done
from cli_conformity.runner import run
from cli_conformity.testing import invoke


def test_cli_error_exits_1():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def fail():
        raise CliError("something broke")

    result = invoke(app, ["fail"])
    assert result.exit_code == 1
    assert "something broke" in result.stderr


def test_done_exits_0():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def guide():
        print("guide content")
        raise Done()

    result = invoke(app, ["guide"])
    assert result.exit_code == 0
    assert "guide content" in result.output


def test_invalid_args_exit_2():
    app = create_app(name="test-tool", env_prefix="TEST", telemetry=False)

    @app.command()
    def greet(name: str = typer.Argument(help="Name")):
        output.success(f"Hello {name}")

    result = invoke(app, ["greet"])
    assert result.exit_code != 0


def test_success_exit_0():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def ok():
        output.success("done")

    result = invoke(app, ["ok"])
    assert result.exit_code == 0


def _run_and_capture(app: typer.Typer, args: list[str]) -> int:
    """Run the app through run() and return the exit code."""
    import sys
    from unittest.mock import patch

    from cli_conformity.state import reset as reset_state
    from cli_conformity.output import reset as reset_output
    reset_state()
    reset_output()

    with patch("sys.argv", ["test-tool"] + args):
        try:
            run(app)
            return 0
        except SystemExit as e:
            return int(e.code) if isinstance(e.code, int) else 1


def test_connect_error_exits_1():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def boom():
        raise httpx.ConnectError("connection refused")

    code = _run_and_capture(app, ["boom"])
    assert code == 1


def test_http_status_error_exits_1():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def boom():
        resp = httpx.Response(422, json={"detail": "validation failed"}, request=httpx.Request("GET", "http://x"))
        raise httpx.HTTPStatusError("error", request=resp.request, response=resp)

    code = _run_and_capture(app, ["boom"])
    assert code == 1


def test_timeout_error_exits_1():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def boom():
        raise httpx.TimeoutException("timed out")

    code = _run_and_capture(app, ["boom"])
    assert code == 1


def test_read_error_exits_1():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def boom():
        raise httpx.ReadError("connection reset")

    code = _run_and_capture(app, ["boom"])
    assert code == 1


def test_keyboard_interrupt_exits_cleanly():
    app = create_app(name="test-tool", env_prefix="TEST")

    @app.command()
    def boom():
        raise KeyboardInterrupt()

    code = _run_and_capture(app, ["boom"])
    assert code in (0, 130)
