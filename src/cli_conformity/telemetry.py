"""Fire-and-forget telemetry for argument parse errors."""

from __future__ import annotations


def report_parse_error(
    argv: list[str],
    error_msg: str,
    server_url: str | None = None,
    endpoint: str = "/cli-errors",
) -> None:
    """POST arg parse failure to server. 2s timeout, silent on any error."""
    if not server_url:
        return
    try:
        import httpx

        httpx.post(
            f"{server_url.rstrip('/')}{endpoint}",
            json={
                "argv": argv,
                "error": error_msg,
                "error_type": "usage_error",
            },
            timeout=2,
        )
    except Exception:
        pass
