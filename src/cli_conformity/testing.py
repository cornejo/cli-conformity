"""Test helper for cli-conformity apps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typer.testing import CliRunner

from .errors import CliError
from .output import reset as reset_output
from .state import reset as reset_state

_runner = CliRunner()


@dataclass
class InvokeResult:
    """Result of a test invocation."""

    exit_code: int
    output: str
    stderr: str


def invoke(
    app: Any,
    args: list[str] | str | None = None,
    env: dict[str, str] | None = None,
    input: str | None = None,
) -> InvokeResult:
    """Invoke a cli-conformity app in tests.

    Handles CliError -> exit 1 and Done -> exit 0, matching production
    behavior. Resets global state between calls.
    """
    reset_state()
    reset_output()

    result = _runner.invoke(
        app,
        args,
        env=env,
        input=input,
        catch_exceptions=True,
    )

    stderr = ""
    if result.exception:
        if isinstance(result.exception, SystemExit):
            raw_code = result.exception.code
            code = raw_code if isinstance(raw_code, int) else (1 if raw_code else 0)
            return InvokeResult(
                exit_code=code,
                output=result.output,
                stderr="",
            )
        if isinstance(result.exception, CliError):
            return InvokeResult(
                exit_code=1,
                output=result.output,
                stderr=f"Error: {result.exception.message}\n",
            )

    return InvokeResult(
        exit_code=result.exit_code,
        output=result.output,
        stderr=stderr,
    )
