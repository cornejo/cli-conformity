"""Tests for handle_response()."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cli_conformity.client import handle_response
from cli_conformity.errors import CliError


def _make_response(status_code: int, json_data: object = None, text: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = Exception("no json")
    return resp


def test_success_returns_json():
    resp = _make_response(200, {"result": "ok"})
    assert handle_response(resp) == {"result": "ok"}


def test_success_returns_text_when_no_json():
    resp = _make_response(200, text="plain text")
    resp.json.side_effect = Exception("not json")
    assert handle_response(resp) == "plain text"


def test_400_raises_cli_error_with_detail():
    resp = _make_response(400, {"detail": "bad request"})
    with pytest.raises(CliError, match="400.*bad request"):
        handle_response(resp)


def test_404_raises_cli_error_with_error_field():
    resp = _make_response(404, {"error": "not found"})
    with pytest.raises(CliError, match="404.*not found"):
        handle_response(resp)


def test_500_with_text_body():
    resp = _make_response(500, text="Internal Server Error")
    with pytest.raises(CliError, match="500.*Internal Server Error"):
        handle_response(resp)


def test_error_code_attribute():
    resp = _make_response(422, {"detail": "validation failed"})
    with pytest.raises(CliError) as exc_info:
        handle_response(resp)
    assert exc_info.value.code == "error"
