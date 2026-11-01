"""CLI layer behaviour: help, version, exit codes, and what is deliberately absent."""

from collections.abc import Callable

from typer.testing import CliRunner

import packproof
from packproof.cli.main import app

runner = CliRunner()


def test_help_describes_the_product_and_lists_the_version_flag(
    normalize_ansi: Callable[[str], str],
) -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    help_text = normalize_ansi(result.stdout)
    assert "Usage: packproof" in help_text
    assert "prove what's inside your packages" in help_text
    assert "--version" in help_text
    assert "--help" in help_text


def test_short_help_flag_is_equivalent_to_long_help() -> None:
    assert runner.invoke(app, ["-h"]).stdout == runner.invoke(app, ["--help"]).stdout


def test_version_flag_reports_the_single_source_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"packproof {packproof.__version__}"


def test_version_short_flag_matches_long_flag() -> None:
    assert runner.invoke(app, ["-V"]).stdout == runner.invoke(app, ["--version"]).stdout


def test_bare_invocation_prints_help_and_signals_usage_error(
    normalize_ansi: Callable[[str], str],
) -> None:
    """`packproof` with no arguments is a usage error: help goes to stdout and the
    process exits 2 rather than pretending a scan ran."""
    result = runner.invoke(app, [])

    assert result.exit_code == 2
    assert "Usage: packproof" in normalize_ansi(result.stdout)


def test_analysis_commands_are_not_implemented_yet() -> None:
    """Milestone 0.1 must not silently accept a command it cannot honor."""
    for command in ("scan", "download", "source", "report"):
        result = runner.invoke(app, [command, "express@4.21.2"])

        assert result.exit_code == 2, command
        assert f"No such command {command!r}" in result.output, command


def test_unknown_option_is_rejected_with_usage_error() -> None:
    result = runner.invoke(app, ["--registry", "https://registry.npmjs.org"])

    assert result.exit_code == 2
