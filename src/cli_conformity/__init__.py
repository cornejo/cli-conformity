"""cli-conformity — enforce consistent CLI interfaces across Typer-based tools."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from .app import create_app
from .client import handle_response
from .errors import CliError, Done
from .guides import GuideOption, show_guide
from .runner import run
from .state import (
    require_project,
    require_server,
    resolve_config,
    resolve_server,
    state,
)
from . import output

ProjectOption = Annotated[
    Optional[str],
    typer.Option("--project", "-p", help="Project name."),
]

JsonOption = Annotated[
    bool,
    typer.Option("--json", "-j", help="Output as JSON."),
]


def sub_app_options(
    project: str | None = None,
    json_output: bool = False,
) -> None:
    """Merge sub-app local flags into global state."""
    if project:
        state.project = project
    if json_output:
        state.json = True


__all__ = [
    "CliError",
    "Done",
    "GuideOption",
    "JsonOption",
    "ProjectOption",
    "create_app",
    "handle_response",
    "output",
    "require_project",
    "require_server",
    "resolve_config",
    "resolve_server",
    "run",
    "show_guide",
    "state",
    "sub_app_options",
]
