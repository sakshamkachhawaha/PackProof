"""Shared pytest configuration.

Applies the `unit` / `integration` marker from the directory a test file lives in, so
`pytest -m unit` works without repeating a decorator on every test function. Adding a
test to `tests/unit/` or `tests/integration/` is the whole declaration of its tier.
"""

import re
from collections.abc import Callable, Sequence

import pytest

TIERS = frozenset({"unit", "integration"})

# ESC [ <params> m — the SGR family, which is the only thing Rich uses to style help text.
# Deliberately not a general escape scrubber: a wider pattern would silently delete real
# output, and a help screen's `[OPTIONS]` must survive whatever the helper does.
_ANSI_SGR = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Remove ANSI SGR sequences, leaving every visible character exactly where it was."""
    return _ANSI_SGR.sub("", text)


def pytest_collection_modifyitems(items: Sequence[pytest.Item]) -> None:
    for item in items:
        tier = item.path.parent.name
        if tier in TIERS:
            item.add_marker(tier)


@pytest.fixture
def normalize_ansi() -> Callable[[str], str]:
    """Strip ANSI styling from terminal output so assertions test what it *says*.

    Typer forces a terminal console when `GITHUB_ACTIONS` is set, so identical help text
    arrives bold and colored in CI and plain locally. Style codes land between `Usage: `
    and the program name, which breaks a literal substring check without any difference in
    behavior — whether the help screen is colored is not a thing this project specifies.
    """
    return _strip_ansi
