import enum
import sys
from pathlib import Path
from typing import Optional

from pm import argparse, commands, config, typedef
from pm.args import Args


def app() -> None:
    print(sys.argv)
    args: Args = argparse.parse()
    print(
        f"""
Args:
    {args.flags=}
    {args.command=}
    {args.project=}
    flags={args.command.get_flags()}
    {args.worktree=}
""")
    print()
    
    args.command.run(args)


if __name__ == "__main__":
    app()
