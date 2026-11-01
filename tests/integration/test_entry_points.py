"""Both documented entry points, executed as real subprocesses.

These are integration tests because they cross a process boundary: interpreter startup,
the installed distribution metadata, and the packaging entry points all have to line up
for `python -m packproof` to work for someone who just cloned the repo.
"""

import os
import subprocess
import sys
from collections.abc import Callable, Mapping
from importlib.metadata import entry_points

import pytest

import packproof

TIMEOUT_SECONDS = 60


def run(*argv: str, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Launch a real interpreter. Callers pass only `sys.executable` and literal
    arguments — never data derived from a scanned package — so the bandit warning
    about untrusted input does not apply here.

    `env=None` inherits this process's environment; passing a mapping affects only the
    child, which is how a test can pose as GitHub Actions without touching global state.
    """
    return subprocess.run(  # noqa: S603
        argv,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        env=env,
    )


@pytest.mark.integration
def test_module_entry_point_prints_help(normalize_ansi: Callable[[str], str]) -> None:
    result = run(sys.executable, "-m", "packproof", "--help")

    assert result.returncode == 0, result.stderr
    assert "Usage: python -m packproof" in normalize_ansi(result.stdout)
    assert "--version" in normalize_ansi(result.stdout)


@pytest.mark.integration
def test_module_entry_point_reports_the_installed_version() -> None:
    result = run(sys.executable, "-m", "packproof", "--version")

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"packproof {packproof.__version__}"


@pytest.mark.integration
def test_console_script_target_and_module_execution_agree() -> None:
    """`packproof` calls `packproof.cli.main:main`; `python -m packproof` calls the same
    function. Invoking the script target directly proves the two cannot drift apart."""
    script_target = run(
        sys.executable,
        "-c",
        "from packproof.cli.main import main; main()",
        "--version",
    )
    module = run(sys.executable, "-m", "packproof", "--version")

    assert script_target.returncode == 0, script_target.stderr
    assert script_target.stdout == module.stdout


@pytest.mark.integration
def test_declared_console_script_entry_point_loads() -> None:
    """A renamed or moved `main` would break the installed command while the tests that
    import it directly stayed green. This test closes that gap."""
    scripts = [ep for ep in entry_points(group="console_scripts") if ep.name == "packproof"]

    assert len(scripts) == 1, f"expected exactly one `packproof` script, got {scripts}"
    assert scripts[0].value == "packproof.cli.main:main"

    loaded = scripts[0].load()
    assert loaded.__module__ == "packproof.cli.main"
    assert loaded.__name__ == "main"


@pytest.mark.integration
def test_module_entry_point_rejects_an_unimplemented_command() -> None:
    result = run(sys.executable, "-m", "packproof", "scan", "express@4.21.2")

    assert result.returncode == 2
    assert "No such command 'scan'" in result.stderr


# ------------------------- the styling GitHub Actions forces (the run that failed CI)


def _github_actions_env() -> dict[str, str]:
    """This environment plus `GITHUB_ACTIONS`, the variable Typer keys its styling on.

    Typer decides `FORCE_TERMINAL` when `rich_utils` is first imported, so patching the
    variable mid-test cannot restyle an in-process `CliRunner` call — the value is already
    frozen. A child interpreter imports the module afresh and renders exactly the way CI
    does, and because the mapping goes to that one child, global state is untouched.
    """
    return {**os.environ, "GITHUB_ACTIONS": "true"}


@pytest.mark.integration
def test_help_survives_the_styling_github_actions_forces(
    normalize_ansi: Callable[[str], str],
) -> None:
    """Enter the failing condition on purpose, and prove which part is doing the work.

    The raw-output assertions are what keep this load-bearing: they state that styling
    really arrived and that the literal fragment really is absent from it. If the helper
    ever stopped stripping escapes, or Typer stopped styling, this test reports which.
    """
    result = run(sys.executable, "-m", "packproof", "--help", env=_github_actions_env())

    assert result.returncode == 0, result.stderr
    assert "\x1b[" in result.stdout
    assert "Usage: python -m packproof" not in result.stdout

    help_text = normalize_ansi(result.stdout)
    assert "Usage: python -m packproof" in help_text
    assert "prove what's inside your packages" in help_text
    assert "--version" in help_text
    assert "--help" in help_text


@pytest.mark.integration
def test_bare_invocation_survives_the_styling_github_actions_forces(
    normalize_ansi: Callable[[str], str],
) -> None:
    """Same condition, the other help path: usage text plus exit code 2, styled."""
    result = run(sys.executable, "-m", "packproof", env=_github_actions_env())

    assert result.returncode == 2
    assert "\x1b[" in result.stdout
    assert "Usage: python -m packproof" not in result.stdout
    assert "Usage: python -m packproof" in normalize_ansi(result.stdout)
