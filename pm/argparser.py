"""Argument parsing module."""

import logging

from pm import commands, utils
from pm.models import Cmd, Flag
from pm.typedef import StrList

logger = logging.getLogger("pm")


def parse(argv: StrList) -> Cmd:
    """Parse system arguments.

    Signature:
        pm [--app-flags] | [cmd [--cmd-flags] proj-name [worktree-name]],  in any order

    Examples:
    $ `pm -h` | --help,  print usage
    $ `pm`, same as `pm ls`
    $ `pm ls -a proj-name [worktree-name]`
    $ `pm open proj-name [worktree-name]`

    $ `pm myproj ls`, will look for project 'myproj' and list all
        - worktrees, if bare repo
        - branches, if git repo
        - perform `ls` command, if not a repo

    """
    MAX_POSITIONAL_ARGS = 4
    app_flag_names = commands.get_app_flag_names()

    # Call without arguments == `ls` command
    if not argv:
        return commands.create_cmd("ls")

    # Check for app flag
    if name := utils.find_in_names(argv[0], app_flag_names):
        return commands.create_app_flag_cmd(name)
    if is_help_name(argv[0]):
        return commands.Help()

    command_names = commands.get_command_names()
    cmd: Cmd | None = None
    positional: StrList = []
    ndx = 0

    while ndx < len(argv):
        arg = argv[ndx]

        if arg.startswith("-"):
            if is_help_name(arg) and cmd:
                return commands.Help(cmd=cmd)
            if not cmd or not cmd.flags:
                raise ValueError(f"Unknown flag {arg}.")

            flag = utils.get_flag_by_name(arg, cmd.flags)
            if not flag:
                raise ValueError(f"Unknown flag {arg} for command {cmd.name}")
            ndx = parse_flag(flag, argv, ndx)
        elif not cmd and arg in command_names:
            cmd = commands.create_cmd(arg)
        else:
            positional.append(arg)
            if len(positional) > MAX_POSITIONAL_ARGS:
                raise ValueError("Too many positional arguments.")
        ndx += 1
    if not cmd:
        raise ValueError("Missing command name")
    if positional:
        cmd.positional = positional
    return cmd


def parse_flag(flag: Flag, argv: StrList, ndx: int) -> int:
    """Consume flag based on flag definition."""
    if isinstance(flag.val, bool):
        flag.val = True
    elif isinstance(flag.val, str):
        flag.val = argv[ndx]
        ndx += 1
    elif isinstance(flag.val, list):
        while ndx < len(argv) and not argv[ndx].startswith("-"):
            flag.val.append(argv[ndx])
            ndx += 1
    else:
        raise TypeError(f"Unsupported flag type {type(flag.val)}")
    return ndx


def is_help_name(flag_name: str) -> bool:
    """Checks if is a help flag."""
    return flag_name in {"-h", "--help"}
