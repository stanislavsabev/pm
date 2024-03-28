"""Handler for calling the `pm` package directly from the command line."""

import logging
import sys
import traceback

from pm import argparse, const
from pm.commands import COMMANDS

logger = logging.getLogger("pm")


def die(msg: str | None) -> None:
    """Print message end exit with error."""
    if msg:
        print(f"{const.APP_NAME}: {msg}")
    sys.exit(1)


def app() -> None:
    """Application entry point."""
    try:
        args = argparse.parse(sys.argv)

        cmd_cls = COMMANDS[args.cmd_name]
        cmd = cmd_cls(args)
        logger.debug(f"Running command {args.cmd_name}")
        cmd.run()
    except Exception:
        die(traceback.format_exc())


if __name__ == "__main__":
    app()
