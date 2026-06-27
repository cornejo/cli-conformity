# cli-conformity

A Python framework for building consistent, well-behaved CLI tools. Built on top of [Typer](https://typer.tiangolo.com/), [httpx](https://www.python-httpx.org/), and [Rich](https://rich.readthedocs.io/).

cli-conformity is opinionated by design. It owns the entry point, error handling, output routing, and telemetry so that every tool built on it behaves identically. You plug in commands; the framework handles everything else.

## Why

If you maintain multiple CLI tools that talk to backend servers, they inevitably diverge: one uses `typer.Exit()`, another calls `sys.exit()`, a third raises `SystemExit`. One formats errors as JSON to stderr, another prints plain text to stdout. One has `--host` and `--port` flags, another has `--server`. Users (and LLMs) have to learn each tool's quirks individually.

cli-conformity eliminates this class of problem. New tools are conformant by default. Existing tools stay conformant because the framework enforces it, not convention.

## Installation

```bash
pip install cli-conformity
```

Requires Python 3.11+.

## Quick Start

```python
# myapp/cli.py
from cli_conformity import create_app, run, output
from cli_conformity.errors import CliError
from cli_conformity.state import require_server

app = create_app(
    name="myapp",
    description="My CLI tool.",
    env_prefix="MYAPP",
    server_default="http://localhost:8000",
)

@app.command()
def status():
    """Show server status."""
    import httpx
    server = require_server()
    resp = httpx.get(f"{server}/status")
    output.data(resp.json())

@app.command()
def greet(name: str):
    """Say hello."""
    output.success(f"Hello, {name}!")

def main():
    run(app)
```

```bash
$ myapp --help
$ myapp --json status
$ myapp --verbose greet World
$ myapp --version
```

That's it. Your tool now has:

- `--verbose` / `-v`, `--json` / `-j`, `--no-color` flags
- `--server` / `-s`, `--api-key`, `--project` / `-p` flags (with env var fallback)
- `--version` flag and `version` subcommand (shows CLI version + server health)
- `config show|set|get|path` subcommands (persistent config at `~/.config/myapp/config.json`)
- Standardized error handling for all httpx exceptions
- Telemetry on argument parse failures (fire-and-forget, opt-out)
- `NO_COLOR` environment variable support
- Dual-mode output (Rich text for humans, JSON for machines)

## Core Concepts

### `run()` is the only exit path

Commands never call `sys.exit()`, `typer.Exit()`, or `raise SystemExit`. Instead, they raise one of two exceptions:

```python
from cli_conformity.errors import CliError, Done

# Signal an error (exit 1)
raise CliError("something went wrong")

# Signal an error with a machine-readable code (exit 1, code in JSON output)
raise CliError("not found", code="not_found")

# Signal non-error early termination (exit 0) — e.g. after printing a guide
raise Done()
```

The `run()` function catches these and translates them to formatted output and appropriate exit codes. It also catches httpx exceptions (`ConnectError`, `HTTPStatusError`, `TimeoutException`, `ReadError`), `KeyboardInterrupt`, and argument parse failures (exit code 2).

This means every tool built on cli-conformity handles network errors, keyboard interrupts, and bad arguments identically — without any per-tool code.

### Config resolution

All configuration follows the same precedence chain:

```
CLI flag  >  environment variable  >  config file  >  default
```

For example, `--server` beats `MYAPP_SERVER`, which beats the value in `~/.config/myapp/config.json`, which beats the `server_default` passed to `create_app()`.

```python
from cli_conformity.state import resolve_config, resolve_server, require_server, require_project

# Generic resolution
value = resolve_config("api_key", cli_value=explicit, default="fallback")

# Server-specific (auto-prefixes http:// if missing)
server = resolve_server()       # returns "" if none configured
server = require_server()       # raises CliError if none configured

# Project-specific (checks state, env, config file)
project = require_project()                    # raises CliError if none found
project = require_project(explicit="my-proj")  # explicit value wins
```

### Dual-mode output

Every output function respects the `--json` flag:

```python
from cli_conformity import output

# Key-value data — Rich formatted text or JSON object
output.data({"name": "Alice", "role": "admin"})

# Tabular data — Rich table or JSON array
output.table(rows, columns=["name", "role", "created_at"], title="Users")

# Success message — green text or {"status": "ok", "message": "..."}
output.success("User created")

# Error message — red text to stderr or {"status": "error", ...} to stderr
output.error("User not found", code="not_found")

# Raw JSON output
output.print_json({"any": "data"})

# Timestamp formatting
output.format_age("2024-01-15T10:30:00Z")  # "3d ago"
```

Rich markup in user-supplied data is automatically escaped to prevent injection.

## API Reference

### `create_app()`

The factory function. Returns a configured `typer.Typer` instance.

```python
app = create_app(
    name="myapp",                                    # Required. Used for config dir, version display.
    env_prefix="MYAPP",                              # Required. Prefix for env vars (MYAPP_SERVER, etc).
    description="My tool.",                          # Help text shown in --help.
    server_default="http://localhost:8000",           # Default server URL.
    health_endpoint="/health",                       # Server health check endpoint for `version` command.
    telemetry_endpoint="/cli-errors",                # Endpoint for parse error telemetry.
    server_flag=True,                                # Include --server/-s flag.
    api_key_flag=True,                               # Include --api-key flag.
    project_flag=True,                               # Include --project/-p flag.
    global_config=True,                              # Register config subcommands + ~/.config dir.
    guide=True,                                      # Enable guide system.
    guides={"topic": "Guide text..."},               # Register guides at creation time.
    telemetry=True,                                  # Post telemetry on arg parse failures.
    known_config_keys={"default-project": "default_project"},  # kebab-case to snake_case mapping.
)
```

Every boolean flag defaults to `True`. Opt out of features that don't apply:

```python
# A tool with no server, no global config, no telemetry
app = create_app(
    name="local-tool",
    env_prefix="LOCAL",
    server_flag=False,
    api_key_flag=False,
    global_config=False,
    telemetry=False,
)
```

### `run(app)`

The entry point. Call this from your `main()` function:

```python
from cli_conformity import create_app, run

app = create_app(name="myapp", env_prefix="MYAPP")

# ... register commands ...

def main():
    run(app)
```

`run()` handles:

| Exception | Behavior |
|---|---|
| `CliError` | Formatted error message, exit 1 |
| `Done` | Silent exit 0 |
| `SystemExit(2)` | Post telemetry (if enabled), re-raise |
| `httpx.ConnectError` | "Cannot connect to server", exit 1 |
| `httpx.HTTPStatusError` | Status code + detail from response body, exit 1 |
| `httpx.TimeoutException` | "Request timed out", exit 1 |
| `httpx.ReadError` | "Server closed the connection", exit 1 |
| `KeyboardInterrupt` | Clean exit |

When `--verbose` is set, httpx exceptions also print the full traceback.

### `handle_response()`

A convenience helper for the common "check status, extract JSON" pattern:

```python
from cli_conformity.client import handle_response

resp = httpx.get(f"{server}/api/users")
data = handle_response(resp)  # Returns resp.json() on 2xx, raises CliError on 4xx/5xx
```

This is not an httpx wrapper. Tools that need raw httpx access (streaming, WebSockets, custom error handling) use httpx directly — the runner catches httpx exceptions regardless.

### Sub-app Options

For Typer sub-apps that need their own `--project` or `--json` flags:

```python
import typer
from cli_conformity import ProjectOption, JsonOption, sub_app_options, output
from cli_conformity.state import require_project

app = typer.Typer(no_args_is_help=True)

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    project: ProjectOption = None,
    json_output: JsonOption = False,
):
    sub_app_options(project=project, json_output=json_output)

@app.command("list")
def list_items():
    proj = require_project()
    # ...
```

`sub_app_options()` merges sub-app flags into the global state, so `require_project()` and `output.data()` work correctly downstream.

### Guides

Register usage guides that users can view with `--guide`:

```python
from cli_conformity import create_app, GuideOption
from cli_conformity.errors import Done
from cli_conformity.guides import show_guide

app = create_app(
    name="myapp",
    env_prefix="MYAPP",
    guides={
        "quickstart": "# Quick Start\n\nRun `myapp init` to get started...",
        "config": "# Configuration\n\nSettings are stored in ~/.config/myapp/...",
    },
)

@app.command()
def init(guide: GuideOption = False):
    """Initialize a new project."""
    if guide:
        show_guide("quickstart")
        raise Done()
    # ... normal init logic ...
```

Guides render with Rich formatting. On a TTY, they use a pager; when piped, they print directly.

### Global State

The `state` singleton holds the resolved values of all global flags:

```python
from cli_conformity.state import state

state.name             # Tool name
state.env_prefix       # Environment variable prefix
state.server           # --server value (or None)
state.api_key          # --api-key value (or None)
state.project          # --project value (or None)
state.verbose          # --verbose flag
state.json             # --json flag
state.no_color         # --no-color flag
state.server_default   # Default server URL from create_app()
state.config_dir       # Config directory path (or None)
```

### Telemetry

When a user (or an LLM) invokes a tool with invalid arguments, the argument parser exits with code 2. If telemetry is enabled, `run()` fires a POST request to the server with the failed `argv` and error message. This is fire-and-forget with a 2-second timeout — it never blocks or crashes the tool.

Telemetry fires **only** on argument parse failures (exit code 2). It does not fire on successful invocations, on `CliError`, or on any other error. Its purpose is to identify how tools are being misused so you can improve the interface.

To disable:

```python
app = create_app(name="myapp", env_prefix="MYAPP", telemetry=False)
```

## Testing

The library provides a test helper that matches production behavior:

```python
from cli_conformity.testing import invoke

def test_greet():
    result = invoke(app, ["greet", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output

def test_missing_arg():
    result = invoke(app, ["greet"])
    assert result.exit_code != 0

def test_error_case():
    result = invoke(app, ["delete", "nonexistent"])
    assert result.exit_code == 1
    assert "not found" in result.stderr
```

`invoke()` wraps Typer's `CliRunner` and intercepts `CliError` (exit 1 with formatted stderr) and `Done` (exit 0). It resets global state between calls automatically. The `InvokeResult` has three fields: `exit_code`, `output` (stdout), and `stderr`.

You can also pass environment variables and stdin:

```python
result = invoke(app, ["status"], env={"MYAPP_SERVER": "http://test.local"})
result = invoke(app, ["login"], input="password\n")
```

## Type Checking

The project is fully typed and passes [pyright](https://github.com/microsoft/pyright) in strict mode. The pyright configuration is in `pyproject.toml`:

```toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
```

## Dependencies

- [typer](https://typer.tiangolo.com/) >= 0.12 — CLI framework (wraps Click)
- [httpx](https://www.python-httpx.org/) >= 0.27 — HTTP client
- [rich](https://rich.readthedocs.io/) >= 13.0 — Terminal formatting

## License

MIT
