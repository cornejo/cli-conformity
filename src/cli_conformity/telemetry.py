"""Fire-and-forget telemetry for argument parse errors."""

from __future__ import annotations


def report_parse_error(
    argv: list[str],
    error_msg: str,
    server_url: str | None = None,
    endpoint: str = "/cli-errors",
    api_key: str | None = None,
) -> None:
    """POST arg parse failure to server. 2s timeout, silent on any error."""
    if not server_url:
        return
    try:
        import httpx

        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        httpx.post(
            f"{server_url.rstrip('/')}{endpoint}",
            json={
                "argv": argv,
                "error": error_msg,
                "error_type": "usage_error",
            },
            headers=headers,
            timeout=2,
        )
    except Exception:
        pass
