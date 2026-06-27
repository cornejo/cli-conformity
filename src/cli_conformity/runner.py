"""run() entry point — the only place sys.exit() is called."""

from __future__ import annotations

import sys
import traceback

import httpx
import typer

from . import output
from .errors import CliError, Done
from .state import resolve_server, state


def run(app: typer.Typer) -> None:
    """Run a cli-conformity app with standardized error handling."""
    try:
        app()
    except Done:
        sys.exit(0)
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code == 2:
            _handle_parse_error(e)
        sys.exit(code)
    except CliError as e:
        output.error(e.message, e.code)
        sys.exit(1)
    except httpx.ConnectError:
        server_url = _resolve_server_silent()
        if server_url:
            output.error(f"Cannot connect to server ({server_url})")
        else:
            output.error("Cannot connect to server")
        if state.verbose:
            traceback.print_exc()
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        try:
            body = e.response.json()
            detail = body.get("detail", body.get("error", str(body)))
        except Exception:
            detail = e.response.text or str(e)
        output.error(f"({status_code}): {detail}")
        if state.verbose:
            traceback.print_exc()
        sys.exit(1)
    except httpx.TimeoutException:
        output.error("Request timed out")
        if state.verbose:
            traceback.print_exc()
        sys.exit(1)
    except httpx.ReadError:
        output.error("Server closed the connection unexpectedly")
        if state.verbose:
            traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)


def _handle_parse_error(exc: SystemExit) -> None:
    """Post telemetry on argument parse failure (exit code 2)."""
    from .app import app_config

    if not app_config.telemetry:
        return
    error_msg = str(exc.__context__) if exc.__context__ else " ".join(sys.argv[1:])
    server_url = _resolve_server_silent()
    if server_url:
        from .telemetry import report_parse_error

        report_parse_error(
            sys.argv,
            error_msg,
            server_url,
            app_config.telemetry_endpoint,
        )


def _resolve_server_silent() -> str | None:
    """Resolve server URL, returning None instead of raising."""
    try:
        url = resolve_server()
        return url or None
    except Exception:
        return None
