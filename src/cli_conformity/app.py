"""create_app() factory — builds a Typer app with standard global flags."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from typer.core import TyperGroup

from .config import make_config_app
from .guides import register_guides
from .state import state
from .version import make_version_command


class _HelpOnErrorGroup(TyperGroup):
    """Click Group that shows the full help text on usage errors."""

    def resolve_command(
        self, ctx: typer.Context, args: list[str],
    ) -> tuple[str | None, Any, list[str]]:
        try:
            return super().resolve_command(ctx, args)
        except Exception as exc:
            typer.echo(ctx.get_help(), err=True)
            typer.echo(err=True)
            if hasattr(exc, "ctx"):
                exc.ctx = None
            raise


class _AppConfig:
    """Internal configuration set by create_app(), read by runner."""

    telemetry: bool = True
    telemetry_endpoint: str = "/cli-errors"
    health_endpoint: str = "/health"
    name: str = ""
    env_prefix: str = ""
    server_default: str = ""
    config_dir: Path | None = None


app_config = _AppConfig()


def _make_version_callback(package_name: str) -> Any:
    def _version_callback(value: bool) -> None:
        if value:
            from importlib.metadata import version as pkg_version

            try:
                v = pkg_version(package_name)
            except Exception:
                v = "dev"
            typer.echo(f"{package_name} {v}")
            raise typer.Exit()

    return _version_callback


def _build_callback(
    *,
    env_prefix: str,
    server_flag: bool,
    api_key_flag: bool,
    project_flag: bool,
    server_default: str,
    description: str,
    version_callback: Any,
) -> Any:
    """Dynamically build a Typer callback with exactly the enabled flags."""
    params: list[str] = []
    body_lines: list[str] = [
        "    from cli_conformity.state import state as _st",
        "    from cli_conformity.app import app_config as _ac",
        "    _st.name = _ac.name",
        "    _st.env_prefix = _ac.env_prefix",
        "    _st.server_default = _ac.server_default",
        "    _st.config_dir = _ac.config_dir",
    ]

    params.append(
        'verbose: bool = typer.Option('
        'False, "--verbose", "-v", help="Show full error tracebacks.")'
    )
    body_lines.append("    _st.verbose = verbose")

    params.append(
        'json_output: bool = typer.Option('
        'False, "--json", "-j", help="Output as JSON.")'
    )
    body_lines.append("    _st.json = json_output")

    params.append(
        'no_color: bool = typer.Option('
        'False, "--no-color", help="Disable colored output.")'
    )
    body_lines.append("    _st.no_color = no_color")

    params.append(
        'version: _t.Optional[bool] = typer.Option('
        'None, "--version", callback=_version_cb, is_eager=True, '
        'help="Show version and exit.")'
    )

    if server_flag:
        params.append(
            f'server: _t.Optional[str] = typer.Option('
            f'None, "--server", "-s", envvar="{env_prefix}_SERVER", '
            f'help="Server URL.")'
        )
        body_lines.append("    _st.server = server")

    if api_key_flag:
        params.append(
            f'api_key: _t.Optional[str] = typer.Option('
            f'None, "--api-key", envvar="{env_prefix}_API_KEY", '
            f'help="API key.")'
        )
        body_lines.append("    _st.api_key = api_key")

    if project_flag:
        params.append(
            f'project: _t.Optional[str] = typer.Option('
            f'None, "--project", "-p", envvar="{env_prefix}_PROJECT", '
            f'help="Active project.")'
        )
        body_lines.append("    _st.project = project")

    sig = ", ".join(params)
    body = "\n".join(body_lines)

    escaped_desc = description.replace("\\", "\\\\").replace('"', '\\"')
    code = f'def _callback({sig}):\n    """{escaped_desc}"""\n{body}\n'

    import typing as _t

    namespace: dict[str, Any] = {
        "typer": typer,
        "_t": _t,
        "_version_cb": version_callback,
    }

    exec(code, namespace)  # noqa: S102
    return namespace["_callback"]


def create_app(
    *,
    name: str,
    description: str = "",
    env_prefix: str,
    server_default: str = "http://localhost:8000",
    health_endpoint: str = "/health",
    telemetry_endpoint: str = "/cli-errors",
    server_flag: bool = True,
    api_key_flag: bool = True,
    project_flag: bool = True,
    global_config: bool = True,
    guide: bool = True,
    guides: dict[str, str] | None = None,
    telemetry: bool = True,
    known_config_keys: dict[str, str] | None = None,
) -> typer.Typer:
    """Create a conformant Typer CLI application.

    Returns a typer.Typer with standard global flags, version subcommand,
    and optionally config subcommands registered.
    """
    app = typer.Typer(
        name=name,
        cls=_HelpOnErrorGroup,
        help=description,
        no_args_is_help=True,
        pretty_exceptions_enable=False,
    )

    state.name = name
    state.env_prefix = env_prefix
    state.server_default = server_default

    if global_config:
        state.config_dir = Path.home() / ".config" / name

    app_config.telemetry = telemetry
    app_config.telemetry_endpoint = telemetry_endpoint
    app_config.health_endpoint = health_endpoint
    app_config.name = name
    app_config.env_prefix = env_prefix
    app_config.server_default = server_default
    app_config.config_dir = state.config_dir

    version_callback = _make_version_callback(name)

    callback_fn = _build_callback(
        env_prefix=env_prefix,
        server_flag=server_flag,
        api_key_flag=api_key_flag,
        project_flag=project_flag,
        server_default=server_default,
        description=description,
        version_callback=version_callback,
    )
    app.callback()(callback_fn)

    version_cmd = make_version_command(name, health_endpoint)
    app.command()(version_cmd)

    if global_config:
        config_app = make_config_app(known_keys=known_config_keys)
        app.add_typer(config_app, name="config", help="Manage CLI configuration.")

    if guides:
        register_guides(guides)

    return app
