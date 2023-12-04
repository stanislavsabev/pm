import sys

from pm import commands
from pm import const
from pm.typedef import LStr

WS4 = const.WS4
WS8 = const.WS8
APP_NAME = const.APP_NAME
HELP = ["-h", "--help"]

_help_flag = f"-h --help{WS8}Show this message and exit."
_short_usage = "\n".join(
    f"{WS8}{name:>5}{WS8}{cmd.short_usage}" for name, cmd in commands.COMMANDS.items()
)
_app_usage = f"""[-h] COMMAND [FLAGS] PROJECT [WORKTREE]

{WS4}Calling `{APP_NAME}`
{WS4}  > without args, lists managed projects (`ls` command).
{WS4}  > with project [worktree], opens a project (`open` command).

{WS4}Commands
{_short_usage}"""
_app_flags: LStr = []


def print_usage(usage: str, flags: LStr) -> None:
    flags.append(_help_flag)
    flags_str = "\n".join(f"{WS4}{flag}" for flag in flags)
    print(
        f"""
{WS4}Usage: {APP_NAME} {usage}

{WS4}Flags
{flags_str}
"""
    )


def parse_app_flag(argv: LStr, ndx: int) -> int:
    flag = argv[ndx]
    ndx += 1
    print(flag)
    return ndx


def parse() -> commands.AppArgs:
    argv = sys.argv[1:]

    args = commands.AppArgs()
    if not argv:  # Called without argument == ls
        cmd_cls = commands.COMMANDS["ls"]
        args.command = cmd_cls()
        return args

    ndx = 0
    flag_parse_fn = parse_app_flag
    while ndx < len(argv):
        if argv[ndx] in HELP:
            if args.command:
                print_usage(args.command.usage, args.command.flags_usage)
            else:
                print_usage(_app_usage, _app_flags)
            sys.exit(0)
        if argv[ndx].startswith("-"):
            ndx = flag_parse_fn(argv, ndx)
        elif not args.command and argv[ndx] in commands.COMMANDS:
            cmd_cls = commands.COMMANDS[argv[ndx]]
            args.command = cmd_cls()
            flag_parse_fn = args.command.parse_flag
        elif not args.name:
            args.name = argv[ndx]
            if not args.command:
                cmd_cls = commands.COMMANDS["open"]
                args.command = cmd_cls()
        elif not args.worktree:
            args.worktree = argv[ndx]
        ndx += 1
    return args
