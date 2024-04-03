"""Handler for calling the `pm` package directly from the command line."""

import logging
import sys

from pm import argparser, const

logger = logging.getLogger("pm")


def die(msg: str | None) -> None:
    """Print message end exit with error."""
    if msg:
        print(f"{const.APP_NAME}: {msg}")
    raise SystemExit


def app() -> None:
    """Application entry point."""
    try:
        cmd = argparser.parse(sys.argv[1:])
        logger.debug(f"Running {cmd.name}")
        cmd.run()
    except Exception as e:
        die(e.args[0])


if __name__ == "__main__":
    app()
