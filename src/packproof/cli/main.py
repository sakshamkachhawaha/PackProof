"""PackProof command-line application.

Only argument handling and presentation live in this module. Each future command
(`scan`, `download`, `source`, `report`) will register itself here and delegate the
work to the module that owns it.

Try:
    packproof --help
    packproof --version
    python -m packproof --help
"""

from typing import Annotated

import typer

from packproof import __version__

app = typer.Typer(
    name="packproof",
    help=(
        "PackProof — prove what's inside your packages.\n\n"
        "Compares a published npm package with the source revision it claims to come "
        "from, so build output and suspicious modification are easy to tell apart.\n\n"
        "Milestone 0.1 ships the project foundation only: analysis commands arrive in "
        "later releases."
    ),
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    # Never dump local variables to the terminal: scans will handle untrusted package
    # content and a traceback with locals could echo it back at the user.
    pretty_exceptions_show_locals=False,
)


def _show_version(value: bool) -> None:
    """Print the version and exit before any command resolution happens."""
    if not value:
        return
    typer.echo(f"packproof {__version__}")
    raise typer.Exit()


@app.callback()
def _root(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=_show_version,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Global options shared by every command.

    Declaring a callback keeps `packproof` a command group, which is what allows
    future commands to be added without changing how the CLI is invoked.
    """


def main() -> None:
    """Invoke the CLI; target of the console script and of `python -m packproof`."""
    app()
