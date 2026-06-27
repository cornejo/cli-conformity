"""Convenience helpers for httpx responses."""

from __future__ import annotations

from typing import Any

import httpx

from .errors import CliError


def handle_response(resp: httpx.Response) -> Any:
    """Check response status and return JSON. Raises CliError on 4xx/5xx."""
    if resp.status_code >= 400:
        try:
            body = resp.json()
            detail = body.get("detail", body.get("error", str(body)))
        except Exception:
            detail = resp.text or str(resp.status_code)
        raise CliError(f"({resp.status_code}): {detail}")
    try:
        return resp.json()
    except Exception:
        raise CliError(f"unexpected response from server (not JSON): {resp.text[:200]}")
