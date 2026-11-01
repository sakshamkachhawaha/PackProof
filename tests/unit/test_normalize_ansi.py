"""The ANSI helper the CLI assertions lean on.

These feed the helper literal escape sequences rather than output captured from a live
terminal, because what matters is what the helper removes — not which palette Rich
happened to pick on a given day. A test that asserted "the 33rd color code becomes the
33rd color code" would be fragile and prove nothing.
"""

from collections.abc import Callable

import pytest


def test_plain_text_is_returned_unchanged(normalize_ansi: Callable[[str], str]) -> None:
    text = "Usage: packproof [OPTIONS] COMMAND [ARGS]..."
    assert normalize_ansi(text) == text


def test_empty_output_stays_empty(normalize_ansi: Callable[[str], str]) -> None:
    assert normalize_ansi("") == ""


def test_colored_text_becomes_readable_plain_text(
    normalize_ansi: Callable[[str], str],
) -> None:
    assert normalize_ansi("\x1b[31mdownload refused\x1b[0m") == "download refused"


@pytest.mark.parametrize(
    ("styled", "visible"),
    [
        ("\x1b[1m\x1b[33mUsage:\x1b[0m packproof", "Usage: packproof"),
        ("\x1b[32mgreen\x1b[0m and \x1b[31mred\x1b[0m", "green and red"),
        ("a\x1b[0mb\x1b[1mc\x1b[38;5;201md", "abcd"),
    ],
)
def test_multiple_sequences_in_one_line_are_all_removed(
    normalize_ansi: Callable[[str], str],
    styled: str,
    visible: str,
) -> None:
    assert normalize_ansi(styled) == visible


def test_text_surrounding_the_sequences_stays_intact(
    normalize_ansi: Callable[[str], str],
) -> None:
    """Spaces, newlines and punctuation are the assertion's subject too, not debris."""
    styled = "  \x1b[1mUsage: \x1b[0m\n  packproof  \n"
    assert normalize_ansi(styled) == "  Usage: \n  packproof  \n"


def test_bracketed_help_placeholders_are_not_escapes(
    normalize_ansi: Callable[[str], str],
) -> None:
    """`[OPTIONS]` and `[ARGS]...` look escape-adjacent and must survive.

    A pattern broad enough to swallow them would make the help assertions pass on gutted
    output — the failure mode that turns a green suite into a meaningless one.
    """
    assert normalize_ansi("[OPTIONS] [COMMAND [ARGS]...] [--version]") == (
        "[OPTIONS] [COMMAND [ARGS]...] [--version]"
    )


def test_the_usage_line_ci_produced_reduces_to_the_asserted_fragment(
    normalize_ansi: Callable[[str], str],
) -> None:
    """The shape GitHub Actions actually emitted, held as a literal.

    The style reset falls between `Usage: ` and the program name, which is precisely why
    the unnormalized substring check failed while the application behaved correctly.
    """
    styled = "\x1b[1m \x1b[0m\x1b[1;33mUsage: \x1b[0m\x1b[1mpackproof\x1b[0m [OPTIONS]"

    assert "Usage: packproof" not in styled
    assert normalize_ansi(styled) == " Usage: packproof [OPTIONS]"
    assert "Usage: packproof" in normalize_ansi(styled)


def test_stripping_is_idempotent(normalize_ansi: Callable[[str], str]) -> None:
    once = normalize_ansi("\x1b[1mUsage: \x1b[0mpackproof")
    assert normalize_ansi(once) == once
