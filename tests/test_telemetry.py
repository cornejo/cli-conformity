"""Tests for telemetry module."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

from cli_conformity.telemetry import report_parse_error


def test_posts_to_server():
    with patch("httpx.post") as mock_post:
        report_parse_error(
            ["mytool", "--bad-flag"],
            "no such option: --bad-flag",
            "http://localhost:8000",
        )
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/cli-errors" in call_args[0][0]
        payload = call_args[1]["json"]
        assert payload["argv"] == ["mytool", "--bad-flag"]
        assert payload["error_type"] == "usage_error"


def test_custom_endpoint():
    with patch("httpx.post") as mock_post:
        report_parse_error(
            ["mytool"], "err", "http://localhost:8000", endpoint="/errors"
        )
        assert "/errors" in mock_post.call_args[0][0]


def test_no_op_when_server_url_is_none():
    with patch("httpx.post") as mock_post:
        report_parse_error(["mytool"], "err", None)
        mock_post.assert_not_called()


def test_silent_on_network_error():
    with patch("httpx.post", side_effect=ConnectionError("refused")):
        report_parse_error(["mytool"], "err", "http://localhost:8000")


def test_strips_trailing_slash():
    with patch("httpx.post") as mock_post:
        report_parse_error(["mytool"], "err", "http://localhost:8000/")
        url = mock_post.call_args[0][0]
        assert url == "http://localhost:8000/cli-errors"
