"""Global CLI state and config resolution."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import CliError


@dataclass
class CliState:
    name: str = ""
    env_prefix: str = ""
    server: str | None = None
    api_key: str | None = None
    project: str | None = None
    verbose: bool = False
    json: bool = False
    no_color: bool = False

    server_default: str = ""
    config_dir: Path | None = None


state = CliState()


def config_path() -> Path | None:
    if state.config_dir is None:
        return None
    return state.config_dir / "config.json"


def load_config() -> dict[str, Any]:
    path = config_path()
    if path and path.exists():
        try:
            return json.loads(path.read_text())  # type: ignore[no-any-return]
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_config(config: dict[str, Any]) -> None:
    path = config_path()
    if path is None:
        raise CliError("No config directory configured")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2) + "\n")


def resolve_config(
    key: str,
    cli_value: str | None = None,
    default: str | None = None,
) -> str | None:
    """Resolve a config value: CLI flag > env var > config file > default."""
    if cli_value is not None:
        return cli_value
    env_key = f"{state.env_prefix}_{key.upper()}"
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val
    if state.config_dir is not None:
        config = load_config()
        if key in config:
            return str(config[key])
    return default


def resolve_server() -> str:
    """Return the resolved server URL."""
    value = resolve_config("server", state.server, state.server_default) or ""
    if value and not value.startswith(("http://", "https://")):
        value = f"http://{value}"
    return value


def require_server() -> str:
    """Like resolve_server but raises CliError if none configured."""
    url = resolve_server()
    if not url:
        raise CliError(
            "No server specified. Use --server or set "
            f"{state.env_prefix}_SERVER."
        )
    return url


def require_project(explicit: str | None = None) -> str:
    """Resolve project: explicit > state > env > config > error."""
    if explicit:
        return explicit
    if state.project:
        return state.project
    env = os.environ.get(f"{state.env_prefix}_PROJECT")
    if env:
        return env
    if state.config_dir is not None:
        config = load_config()
        default = config.get("default_project")
        if default:
            return str(default)
    raise CliError(
        "No project specified. Use --project or set a default with "
        f"'{state.name} config set default-project <name>'"
    )


def reset() -> None:
    """Reset state to defaults (for testing)."""
    state.name = ""
    state.env_prefix = ""
    state.server = None
    state.api_key = None
    state.project = None
    state.verbose = False
    state.json = False
    state.no_color = False
    state.server_default = ""
    state.config_dir = None
