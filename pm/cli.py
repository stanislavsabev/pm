from pm import argparse
from pm import commands


def app() -> None:
    args: commands.AppArgs = argparse.parse()
    if args.command:
        args.command.run(args)


if __name__ == "__main__":
    app()
