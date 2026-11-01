"""Central logging configuration.

Call `configure_logging()` once, from the CLI, before doing work. Every other module
just takes a logger with `logging.getLogger(__name__)`: because those names start with
`packproof.`, they inherit the level, formatter and destination configured on the
`packproof` root logger and never need to configure anything themselves.

Nothing here calls `logging.basicConfig()` — that would mutate global state and fight
with any library that configures logging later.

Log records should carry package names, versions, hashes and finding identifiers.
They must never carry registry tokens, AI provider keys or other credentials; do not
interpolate a `Settings` field into a message without checking that it is not secret.
"""

import logging
import sys
from typing import TextIO

ROOT_LOGGER_NAME = "packproof"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Levels a user may ask for on the command line. `NOTSET` is excluded: it means
# "inherit", which is not a choice anyone should configure by name.
CONFIGURABLE_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def configure_logging(level: int | str = "INFO", *, stream: TextIO | None = None) -> logging.Logger:
    """Attach a stderr handler to the `packproof` logger and return it.

    Idempotent: calling it again replaces the handler instead of stacking duplicates,
    so a repeated call does not double every log line.

    Args:
        level: Level name (case-insensitive) or a `logging` level number.
        stream: Destination stream, for tests. Defaults to stderr so logs and
            report output on stdout stay separable and pipe-friendly.

    Raises:
        ValueError: If `level` is not a configurable level name.
    """
    resolved_level = _resolve_level(level)
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    logger.setLevel(resolved_level)

    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stderr if stream is None else stream)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def _resolve_level(level: int | str) -> int:
    if isinstance(level, int):
        return level
    name = level.strip().upper()
    if name not in CONFIGURABLE_LEVELS:
        choices = ", ".join(CONFIGURABLE_LEVELS)
        raise ValueError(f"unknown log level {level!r}; choose one of: {choices}")
    return logging.getLevelName(name)
