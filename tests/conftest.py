"""Shared fixtures for cli-conformity tests."""

from __future__ import annotations

import pytest

from cli_conformity.guides import reset as reset_guides
from cli_conformity.output import reset as reset_output
from cli_conformity.state import reset as reset_state


@pytest.fixture(autouse=True)
def _clean_state():
    """Reset global state before each test."""
    reset_state()
    reset_output()
    reset_guides()
    yield
    reset_state()
    reset_output()
    reset_guides()
