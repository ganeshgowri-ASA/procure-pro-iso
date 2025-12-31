"""Test fixtures for RFQ document parser tests."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent


def get_fixture_path(filename: str) -> Path:
    """Get the full path to a fixture file."""
    return FIXTURES_DIR / filename
