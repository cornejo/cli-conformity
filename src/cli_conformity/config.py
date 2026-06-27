"""Config subcommand factory — config show|set|get|path."""

from __future__ import annotations

import typer

from . import output
from .state import load_config, save_config


def make_config_app(
    known_keys: dict[str, str] | None = None,
) -> typer.Typer:
    """Create the 'config' sub-app with show/set/get/path commands."""
    app = typer.Typer(no_args_is_help=True)

    keys = known_keys or {}

    def _normalize(key: str) -> str:
        return keys.get(key, key)

    @app.command("show")
    def config_show() -> None:  # pyright: ignore[reportUnusedFunction]
        """Show all configuration values."""
        config = load_config()
        output.data(config)

    @app.command("set")
    def config_set(  # pyright: ignore[reportUnusedFunction]
        key: str = typer.Argument(help="Config key to set."),
        value: str = typer.Argument(help="Value to set."),
    ) -> None:
        """Set a configuration value."""
        config_key = _normalize(key)
        config = load_config()
        config[config_key] = value
        save_config(config)
        output.success(f"Set {config_key} = {value}")

    @app.command("get")
    def config_get(  # pyright: ignore[reportUnusedFunction]
        key: str = typer.Argument(help="Config key to read."),
    ) -> None:
        """Get a configuration value."""
        config_key = _normalize(key)
        config = load_config()
        value = config.get(config_key)
        output.data({config_key: value})

    @app.command("path")
    def config_path() -> None:  # pyright: ignore[reportUnusedFunction]
        """Show the config file path."""
        from .errors import CliError
        from .state import config_path as get_config_path

        path = get_config_path()
        if not path:
            raise CliError("No config directory configured")
        output.data({"path": str(path)})

    return app
