"""Tests for guide system."""

from __future__ import annotations

from cli_conformity import create_app
from cli_conformity.guides import _guides, register_guides, show_guide
from cli_conformity.testing import invoke


def test_register_and_show(capsys):
    register_guides({"topic1": "Guide content for topic 1"})
    assert "topic1" in _guides
    show_guide("topic1")
    captured = capsys.readouterr()
    assert "Guide content for topic 1" in captured.out


def test_show_unknown_guide(capsys):
    show_guide("nonexistent")
    captured = capsys.readouterr()
    assert "No guide for 'nonexistent'" in captured.err


def test_guides_via_create_app():
    app = create_app(
        name="test-tool",
        env_prefix="TEST",
        guides={"myguide": "Hello from the guide"},
    )
    assert "myguide" in _guides


def test_reset_clears_guides():
    register_guides({"a": "b"})
    from cli_conformity.guides import reset
    reset()
    assert len(_guides) == 0
