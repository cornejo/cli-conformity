# Changelog

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
