from pm import argparse
from pm.app_args import AppArgs


def app() -> None:
    args: AppArgs = argparse.parse()
    if args.command:
        args.command.run(args)


if __name__ == "__main__":
    app()
