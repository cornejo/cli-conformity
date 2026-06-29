# Changelog

## 0.1.7 - 2026-06-29

### Fixed
- Sub-command groups (e.g. `ghidranet project`) now show help instead of a "Missing command" error when invoked without a subcommand.

## 0.1.6 - 2026-06-28

### Fixed
- `output.data()` no longer wraps string payloads via Rich's `console.print()`, which corrupted raw data (e.g. JSON from `exec` commands) by inserting newlines at terminal width boundaries.

## 0.1.5 - 2026-06-27

### Fixed
- Removed direct `import click` that broke with Typer 0.26 (which bundles click internally). All click usage replaced with Typer equivalents.

## 0.1.4 - 2026-06-27

### Added
- Unknown commands now display the full help text (with available commands listed) before the error message.

### Fixed
- `handle_response()` now raises `CliError` when a 2xx response is not JSON, instead of silently returning raw text.

## 0.1.3 - 2026-06-27

### Improved
- `format_age()` now returns months (`6mo ago`) and years (`1y ago`) instead of large day counts for older timestamps.

## 0.1.2 - 2026-06-27

### Fixed
- Telemetry no longer fires on no-args help display (exit code 2 with no parse error context). Only actual argument parse failures trigger telemetry.

## 0.1.1 - 2026-06-27

### Fixed
- Telemetry POST to `/cli-errors` now includes `Authorization: Bearer <key>` header when an API key is configured, allowing it to work with auth-required servers.

### Added
- `py.typed` marker for PEP 561 typed package support.

## 0.1.0 - 2026-06-26

Initial release.

### Added
- `create_app()` factory with dynamic callback generation for consistent global flags (`--server`, `--api-key`, `--project`, `--verbose`, `--json`, `--no-color`).
- `run()` entry point with unified error handling for `CliError`, `Done`, httpx exceptions, and `KeyboardInterrupt`.
- Dual-mode output module (`data`, `table`, `success`, `error`, `format_age`) supporting Rich and JSON output.
- Config sub-app (`config show|set|get|path`) with CLI > env var > config file > default resolution.
- Version sub-command with server health check.
- Guide system for `--guide` flags on sub-apps.
- Fire-and-forget telemetry on argument parse failures (exit code 2).
- `handle_response()` convenience helper for HTTP response checking.
- `invoke()` test helper wrapping `CliRunner` with `CliError`/`Done` interception.
- `ProjectOption`, `JsonOption`, `sub_app_options()` type aliases for sub-app callbacks.
