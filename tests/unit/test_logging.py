"""Logging configuration: levels, handlers, inheritance, idempotency, stream choice."""

import io
import logging
from collections.abc import Iterator

import pytest

from packproof.utils.logging import ROOT_LOGGER_NAME, configure_logging


@pytest.fixture(autouse=True)
def restore_packproof_logger() -> Iterator[None]:
    """`configure_logging` mutates a process-wide logger; restore it between tests."""
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    saved_level, saved_handlers, saved_propagate = (
        logger.level,
        list(logger.handlers),
        logger.propagate,
    )
    yield
    logger.handlers[:] = saved_handlers
    logger.setLevel(saved_level)
    logger.propagate = saved_propagate


def test_defaults_to_info_and_renders_level_and_logger_name() -> None:
    stream = io.StringIO()
    logger = configure_logging(stream=stream)

    assert logger.level == logging.INFO
    logger.warning("hash mismatch in %s", "index.js")

    line = stream.getvalue()
    assert "WARNING" in line
    assert "packproof" in line
    assert "hash mismatch in index.js" in line


def test_messages_below_the_configured_level_are_dropped() -> None:
    stream = io.StringIO()
    logger = configure_logging("WARNING", stream=stream)

    logger.debug("inspecting %s", "left-pad@1.3.0")
    assert stream.getvalue() == ""

    logger.error("download refused")
    assert "download refused" in stream.getvalue()


def test_level_names_are_case_insensitive_and_may_be_given_as_numbers() -> None:
    assert configure_logging("debug").level == logging.DEBUG
    assert configure_logging(logging.ERROR).level == logging.ERROR


def test_unconfigurable_level_name_is_rejected_with_choices() -> None:
    with pytest.raises(ValueError, match="unknown log level 'VERBOSE'"):
        configure_logging("VERBOSE")


def test_reconfiguration_replaces_handlers_instead_of_stacking_them() -> None:
    first, second = io.StringIO(), io.StringIO()
    configure_logging("INFO", stream=first)
    logger = configure_logging("INFO", stream=second)

    assert len(logger.handlers) == 1
    logger.info("scan started")

    assert first.getvalue() == ""
    assert second.getvalue().count("scan started") == 1


def test_child_module_loggers_inherit_the_configuration() -> None:
    """Future modules only need `logging.getLogger(__name__)` to be configured."""
    stream = io.StringIO()
    configure_logging("INFO", stream=stream)

    logging.getLogger("packproof.fetchers.npm").info("fetched manifest")

    assert "packproof.fetchers.npm: fetched manifest" in stream.getvalue()


def test_records_do_not_escape_to_the_root_logger() -> None:
    """Propagating would let an embedding application's handlers see our records."""
    logger = configure_logging("INFO", stream=io.StringIO())
    assert logger.propagate is False


def test_logs_go_to_stderr_so_stdout_stays_clean_for_report_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO")
    logging.getLogger(ROOT_LOGGER_NAME).info("wrote 3 findings")

    captured = capsys.readouterr()
    assert "wrote 3 findings" in captured.err
    assert captured.out == ""
