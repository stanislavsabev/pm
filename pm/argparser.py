"""Argument parsing module."""

from pm import commands, models, printer
from pm.typedef import StrList
from pm.utils import is_help_flag


def parse_cmd(argv: StrList) -> tuple[type[models.CmdProto], StrList]:
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
    if not argv:  # Called without argument == ls
        cmd_name = "-ls"
    elif is_help_flag(argv[0]):
        printer.print_app_usage(exit_=True)
    else:
        arg = argv[0]
        if not arg.startswith("-"):
            argv.insert(0, "-open")
        cmd_name = argv[0]
        argv = argv[1:]

    cmd_cls = commands.COMMANDS.get(cmd_name)
    if not cmd_cls:
        raise ValueError(f"Unknown command {arg}")
    return cmd_cls, argv
