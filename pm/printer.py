"""Argument parsing module."""

import sys

from pm import __version__, commands, config, const
from pm.models import Proj, ProjDict, Usage
from pm.proj_man import get_non_managed
from pm.typedef import StrDict, StrListDict

app_usage = Usage(
    header="pm [-h] COMMAND [FLAGS] PROJECT [WORKTREE]",
    description=[
        f"Calling `{const.APP_NAME}`",
        "  > without args, lists managed projects (`ls` command).",
        "  > with project [worktree], opens a project (`open` command).",
    ],
    flags={"-h --help": ["Show this message and exit."]},
)


def print_app_usage(exit_: bool = False) -> None:
    """Print app usage help.

    Args:
        exit_: bool, exit the program after print
    """
    print_usage(app_usage)
    print_commands()
    if exit_:
        sys.exit(0)


def print_commands() -> None:
    """Print list of all commands."""
    print()
    print("Commands")
    for name, cmd in commands.COMMANDS.items():
        if name == "app_help":
            continue
        print(f"  {name}\t  {cmd.usage.short}")


def print_usage(usage: Usage, exit_: bool = False) -> None:
    """Print usage and flags.

    Args:
        usage: Usage model
        exit_: bool, exit the program after print
    """
    print(f"Usage: {usage.header}")

    for line in usage.description:
        print(f"  {line}")

    print_flags(usage.flags)
    if exit_:
        sys.exit(0)


def print_flags(flags: StrListDict) -> None:
    """Print flags.

    Args:
        flags: dict with flags, flags descriptions
    """
    print()
    for name, lines in flags.items():
        line = lines[0] if lines else ""
        print(f"  {name}\t{line}")
        if len(lines) > 1:
            for line in lines[1:]:
                print(f"\t\t  {line}")


# @util.timeit
def print_project(proj: Proj) -> None:
    """Print project formatted info."""
    formatted_branches = []
    is_bare = False
    if proj.git:
        branches = proj.git.worktrees or proj.git.branches

        if branches:
            for branch in branches:
                branch_str = f"(*{branch})" if branch == proj.git.active_branch else f"({branch})"
                formatted_branches.append(branch_str)
        is_bare = proj.git.is_bare
    name = proj.name
    ljust = config.ljust()
    rjust = config.rjust()
    if len(name) > ljust:
        name = ".." + name[-ljust + 2 :]
    print(
        "{short:<{rjust}} | {name:<{ljust}} {bare}: {branches}".format(
            short=proj.short,
            rjust=rjust,
            ljust=ljust,
            name=name,
            bare="b" if is_bare else " ",
            branches=" ".join(formatted_branches),
        )
    )


# @util.timeit
def print_managed(projects: ProjDict) -> None:
    """Print formatted info for the managed projects."""
    print("> Projects:\n")
    if not projects:
        print("  na")
        return
    for project in sorted(projects.values(), key=lambda p: p.short.lower()):
        print_project(project)


# @util.timeit
def print_non_managed(dirs: StrDict) -> None:
    """Print formatted info for the non-managed projects."""
    non_managed = get_non_managed()
    if not non_managed:
        return

    for group in dirs:
        projects = non_managed[group]
        print(f"\n> {group}:\n")
        ljust = config.ljust()
        for i, project in enumerate(sorted(projects, key=str.lower)):
            if i % 2 == 0:
                end = "" if i < len(projects) - 1 else "\n"
                print(f"{project:<{ljust}} |", end=end)
            else:
                print(f" {project}", end="\n")


def print_package_version() -> None:
    """Prints package version."""
    print(__version__)
