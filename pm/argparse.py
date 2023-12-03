import sys

from pm import commands, config
from pm.args import Args

HELP = ["-h", "--help"]
app_help=f""


def print_app_usage():
    print(
        f"""
Usage: {config.APP_NAME} [-h] COMMAND [ARGS] PROJECT [WORKTREE]

Calling `{config.APP_NAME}` without args will list managed projects.
"""
)


def parse_app_flag(argv, ndx):
    flag = argv[ndx]

    ndx += 1
    print(flag)
    return ndx


def parse() -> Args:
    argv = sys.argv[1:]

    args = Args()
    if not argv:  # Called without argument == ls
        cmd_cls = commands.COMMANDS["ls"]
        args.command = cmd_cls()
        return args

    ndx = 0
    flag_parse_fn = parse_app_flag
    while ndx < len(argv):
        if argv[ndx] in HELP:
            if args.command:
                args.command.print_usage()
            else:
                print_app_usage()
            sys.exit(0)
        if argv[ndx].startswith("-"):
            ndx += flag_parse_fn(argv, ndx)
        elif argv[ndx] in commands.COMMANDS:
            cmd_cls = args.commands[argv[ndx]]
            args.command = cmd_cls()
            flag_parse_fn = args.command.parse_flag
        elif not args.project:
            args.project = argv[ndx]
        elif not args.worktree:
            args.worktree = argv[ndx]
        ndx += 1
    return args
