"""Argument parsing module."""

import sys

from pm import __version__, config, utils
from pm.models import Flags, Proj, ProjDict, TCmd, Usage
from pm.typedef import StrDict, StrListDict


def print_commands(commands: list[TCmd]) -> None:
    """Print list of all commands."""
    print()
    print("  Commands")
    for cmd in commands:
        print(f"  {cmd.name:>8}\t{cmd.usage.short}")


def print_usage(usage: Usage, exit_: bool = False) -> None:
    """Print usage and flags.

    Args:
        usage: Usage model
        exit_: bool, exit the program after print
    """
    print(f"Usage: {usage.header}")
    for line in usage.description:
        print(f"  {line}")
    if usage.positional:
        print_positional(usage.positional)

    if exit_:
        sys.exit(0)


def print_positional(positional: list[tuple[str, list[str]]]) -> None:
    """Print positional arguments."""
    print()
    for argname, description in positional:
        print(f"  {argname}\t{description[0]}")
        for line in description[1:]:
            print(f"  \t\t{line}")


def print_flags(flags: Flags) -> None:
    """Print flags.

    Args:
        flags: Flags, flags definitions
    """
    print()
    for flag in flags:
        names = " ".join(utils.expand_flag_name(flag.name))
        if not flag.usage:
            print(f"  {names}")
            return
        usage = flag.usage
        header = usage.header
        if usage.arg:
            names += f"\t{usage.arg}"
        print(f"  {names}\t{header}")
        for line in usage.description:
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
def print_non_managed(dirs: StrDict, non_managed: StrListDict) -> None:
    """Print formatted info for the non-managed projects."""
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
