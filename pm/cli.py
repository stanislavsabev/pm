"""Handler for calling the `pm` package directly from the command line."""

import logging
import sys
import traceback

from pm import argparser, const

logger = logging.getLogger("pm")


def die(msg: str | None) -> None:
    """Print message end exit with error."""
    if msg:
        print(f"{const.APP_NAME}: {msg}")
    sys.exit(1)


def app() -> None:
    """Application entry point."""
    try:
        cmd_cls, argv = argparser.parse_cmd(sys.argv[1:])
        cmd = cmd_cls()
        cmd.parse_args(argv)
        logger.debug(f"Running command {cmd_cls.__name__}")
        cmd.run()
    except Exception:
        die(traceback.format_exc(limit=4))


if __name__ == "__main__":
    app()
