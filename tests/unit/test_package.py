"""Package-level contract: import surface and single-source version."""

import re

import packproof
from packproof import __version__


def test_package_exposes_version_on_import() -> None:
    assert packproof.__version__ == __version__
    assert isinstance(__version__, str)
    assert re.fullmatch(r"\d+\.\d+\.\d+(rc\d+)?", __version__), __version__
    assert packproof.__all__ == ["__version__"]


def test_source_version_matches_installed_distribution_metadata() -> None:
    """Guards the `[tool.hatch.version]` wiring in pyproject.toml.

    If the build ever stops reading the literal in `src/packproof/__init__.py`, the
    installed metadata and the runtime attribute drift apart and this fails.
    """
    from importlib.metadata import version

    assert version("packproof") == __version__


def test_package_has_no_side_effects_at_import_time() -> None:
    """Importing must not configure logging — the CLI owns that decision."""
    import logging

    packproof_spec = logging.Logger.manager.loggerDict.get("packproof")
    handlers = getattr(packproof_spec, "handlers", [])
    assert handlers == [], f"importing packproof attached handlers: {handlers}"
