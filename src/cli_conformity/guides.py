"""Guide system — register and display rich-formatted usage guides."""

from __future__ import annotations

import sys
from typing import Annotated

import typer

_guides: dict[str, str] = {}


GuideOption = Annotated[
    bool,
    typer.Option("--guide", help="Show usage guide."),
]


def reset() -> None:
    """Clear registered guides (for testing)."""
    _guides.clear()


def register_guides(guides: dict[str, str]) -> None:
    """Register guide text keyed by topic name."""
    _guides.update(guides)


def show_guide(name: str) -> None:
    """Render a guide via Rich Console, with pager for TTY."""
    text = _guides.get(name)
    if not text:
        from .output import error_console

        error_console().print(f"[red]No guide for '{name}'[/red]")
        return

    from .output import console as get_console

    con = get_console()
    if sys.stdout.isatty():
        with con.pager(styles=True):
            con.print(text)
    else:
        con.print(text)
