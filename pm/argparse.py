"""Argument parsing module."""

import sys
from dataclasses import dataclass, field

from pm import commands, const, proto
from pm.typedef import StrList

APP_NAME = const.APP_NAME
HELP_FLAGS = ["-h", "--help"]


@dataclass
class Args:
    """Command arguments."""

    cmd_name: str
    proj_name: str | None = None
    worktree: str | None = None

    cmd_flags: StrList = field(default_factory=list)


def print_usage(cmd: proto.CmdProto | None = None) -> None:
    """Print usage and flags."""

    _short_usage = "\n".join(
        f"{const.WS8}{name:>5}{const.WS8}{cmd.usage.short}"
        for name, cmd in commands.COMMANDS.items()
    )
    usage = f"""[-h] COMMAND [FLAGS] PROJECT [WORKTREE]

    {const.WS4}Calling `{APP_NAME}`
    {const.WS4}  > without args, lists managed projects (`ls` command).
    {const.WS4}  > with project [worktree], opens a project (`open` command).

    {const.WS4}Commands
    {_short_usage}"""

    flags = []

    if cmd:
        usage = cmd.usage.full
        flags = cmd.usage.flags

    flags.append(f"-h --help{const.WS8}Show this message and exit.")
    flags_str = "\n".join(f"{const.WS4}{flag}" for flag in flags)
    print(
        f"""
{const.WS4}Usage: {APP_NAME} {usage}

{const.WS4}Flags
{flags_str}
"""
    )


def parse_app_flag(argv: StrList, ndx: int) -> int:
    """Parse application flag."""
    flag = argv[ndx]
    ndx += 1
    print(flag)
    return ndx


def parse(argv: StrList) -> Args:
    """Parse system arguments.
    Signature:
        pm [-cmd] [--cmd-flags] [proj-name [worktree-name]],  in any order

    Examples:
    $ `pm -h` | --help,  print usage
    $ `pm`, same as `pm -ls`
    $ `pm proj-name [worktree-name]`, same as `pm -open proj-name [worktree-name]`

    $ `pm myproj -ls`, will look for project 'myproj' and list all
        - worktrees, if bare repo
        - branches, if git repo
        - perform `ls` command, if not a repo

    """
    if argv and argv[0] in HELP_FLAGS:
        print_usage()
        sys.exit(0)

    if not argv:  # Called without argument == ls
        return Args(cmd_name="-ls")

    cmd_name = ""
    cmd_flags = []
    proj = None
    wt = None

    ndx = 0
    while ndx < len(argv):
        arg = argv[ndx]
        if arg.startswith("-"):
            if not cmd_name and arg in commands.COMMANDS:
                cmd_name = arg
            elif cmd_name:
                cmd_flags.append(arg)
            else:
                raise ValueError(f"Unknown flag '{arg}'")
        elif not proj:
            proj = argv[ndx]
        elif not wt:
            wt = argv[ndx]
        else:
            raise ValueError("Too many positional arguments, see -h for usage")
        ndx += 1
    if not cmd_name:
        raise ValueError("Could not match command to execute.")
    return Args(cmd_name=cmd_name, proj_name=proj, worktree=wt, cmd_flags=cmd_flags)
