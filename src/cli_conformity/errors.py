"""Exceptions for cli-conformity.

Commands raise these instead of sys.exit() / typer.Exit().
"""

from __future__ import annotations


class CliError(Exception):
    """Raised to signal a user-visible error (exit 1)."""

    def __init__(self, message: str, *, code: str = "error"):
        self.message = message
        self.code = code
        super().__init__(message)


class Done(SystemExit):
    """Non-error early termination (e.g. --guide printed).

    Inherits SystemExit so Typer/Click don't treat it as unhandled.
    """

    def __init__(self) -> None:
        super().__init__(0)
