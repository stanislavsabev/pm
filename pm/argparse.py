"""Argument parsing module."""

import sys
from dataclasses import dataclass, field

from pm import commands, const, proto
from pm.typedef import StrList

WS4 = const.WS4
WS8 = const.WS8
APP_NAME = const.APP_NAME
HELP_FLAGS = ["-h", "--help"]


@dataclass
class Args:
    """Command arguments."""

    cmd: proto.CmdProto
    proj_name: str | None = None
    worktree: str | None = None

    flags: StrList = field(default_factory=list)


def print_usage(cmd: proto.CmdProto | None = None) -> None:
    """Print usage and flags."""

    _short_usage = "\n".join(
        f"{WS8}{name:>5}{WS8}{cmd.usage.short}" for name, cmd in commands.COMMANDS.items()
    )
    usage = f"""[-h] COMMAND [FLAGS] PROJECT [WORKTREE]

    {WS4}Calling `{APP_NAME}`
    {WS4}  > without args, lists managed projects (`ls` command).
    {WS4}  > with project [worktree], opens a project (`open` command).

    {WS4}Commands
    {_short_usage}"""

    flags = []

    if cmd:
        usage = cmd.usage.full
        flags = cmd.usage.flags

    flags.append(f"-h --help{WS8}Show this message and exit.")
    flags_str = "\n".join(f"{WS4}{flag}" for flag in flags)
    print(
        f"""
{WS4}Usage: {APP_NAME} {usage}

{WS4}Flags
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
        return Args(cmd=commands.Ls())

    cmd: proto.CmdProto = commands.UnknownCommand()
    proj = None
    wt = None

    ndx = 0
    while ndx < len(argv):
        arg = argv[ndx]
        if arg.startswith("-"):
            if cmd is None and arg in commands.COMMANDS:
                cmd_cls = commands.COMMANDS[arg]
                cmd = cmd_cls()
            elif cmd:
                # parse command args
                ndx = cmd.parse_argv(argv, ndx)
            else:
                raise ValueError(f"Unknown flag '{arg}'")
        elif not proj:
            proj = argv[ndx]
        elif not wt:
            wt = argv[ndx]
        else:
            raise ValueError("Too many positional arguments, see -h for usage")
        ndx += 1

    return Args(cmd=cmd, proj_name=proj, worktree=wt)
