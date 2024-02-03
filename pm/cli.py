"""Handler for calling the `pm` package directly from the command line."""
import logging
import sys
import traceback

from pm import argparse
from pm import commands
from pm import const

logger = logging.getLogger("pm")


def die(msg: str | None) -> None:
    """Print message end exit with error."""
    if msg:
        print(f"{const.APP_NAME}: {msg}")
    sys.exit(1)


def app() -> None:
    """Application entry point."""
    try:
        args: commands.AppArgs = argparse.parse()
        if args.command:
            logger.debug(f"Running command {args.command}")
            args.command.run(args)
    except Exception:
        die(traceback.format_exc())


if __name__ == "__main__":
    app()
