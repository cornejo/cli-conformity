"""Version subcommand factory."""

from __future__ import annotations

from typing import Any, Callable

from . import output
from .state import resolve_server


def make_version_command(
    package_name: str,
    health_endpoint: str = "/health",
) -> Callable[[], None]:
    """Create a 'version' command that shows CLI + server version."""

    def version() -> None:
        """Show CLI version and server health."""
        from importlib.metadata import version as pkg_version

        try:
            cli_version = pkg_version(package_name)
        except Exception:
            cli_version = "dev"

        info: dict[str, Any] = {"cli_version": cli_version}

        server_url = resolve_server()
        if server_url:
            try:
                import httpx

                resp = httpx.get(
                    f"{server_url.rstrip('/')}{health_endpoint}",
                    timeout=5,
                )
                info["server"] = resp.json()
            except Exception:
                info["server"] = "unreachable"

        output.data(info)

    return version
