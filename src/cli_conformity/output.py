"""Output formatting — text and JSON modes, respects --no-color and NO_COLOR."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, cast

from rich.console import Console
from rich.table import Table


_console: Console | None = None
_error_console: Console | None = None


def _no_color() -> bool:
    from .state import state
    return state.no_color or os.environ.get("NO_COLOR") is not None


def _json_mode() -> bool:
    from .state import state
    return state.json


def console() -> Console:
    global _console
    if _console is None or _console.no_color != _no_color():
        _console = Console(no_color=_no_color())
    return _console


def error_console() -> Console:
    global _error_console
    if _error_console is None or _error_console.no_color != _no_color():
        _error_console = Console(stderr=True, no_color=_no_color())
    return _error_console


def reset() -> None:
    """Reset cached consoles (for testing)."""
    global _console, _error_console
    _console = None
    _error_console = None


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def success(message: str) -> None:
    if _json_mode():
        print_json({"status": "ok", "message": message})
    else:
        console().print(f"[green]{message}[/green]")


def error(message: str, code: str = "error") -> None:
    if _json_mode():
        import sys
        print(json.dumps({"status": "error", "code": code, "message": message}, indent=2, default=str), file=sys.stderr)
    else:
        error_console().print(f"[red]Error:[/red] {message}")


def data(payload: Any) -> None:
    if _json_mode():
        print_json(payload)
    elif isinstance(payload, list):
        for item in cast(list[Any], payload):
            if isinstance(item, dict):
                _print_item(cast(dict[str, Any], item))
            else:
                console().print(item)
    elif isinstance(payload, dict):
        _print_item(cast(dict[str, Any], payload))
    else:
        console().print(payload)


def table(
    rows: list[dict[str, Any]],
    columns: list[str],
    title: str | None = None,
) -> None:
    if _json_mode():
        print_json(rows)
        return
    t = Table(title=title)
    for col in columns:
        t.add_column(col)
    for row in rows:
        t.add_row(*[str(row.get(col, "")) for col in columns])
    console().print(t)


def _print_item(item: dict[str, Any]) -> None:
    from rich.markup import escape
    for key, value in item.items():
        console().print(f"  [bold]{key}:[/bold] {escape(str(value))}")
    console().print()


def format_age(ts: str | None) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        secs = int(delta.total_seconds())
        if secs < 60:
            return f"{secs}s ago"
        if secs < 3600:
            return f"{secs // 60}m ago"
        if secs < 86400:
            return f"{secs // 3600}h ago"
        return f"{secs // 86400}d ago"
    except (ValueError, TypeError):
        return ts
