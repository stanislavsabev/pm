"""Argument parsing module."""

import sys

from pm import __version__, config, utils
from pm.models import BCColors, Flags, PrintableProj, Proj, ProjDict, Table, TCmd, Usage
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


def proj_to_printable(proj: Proj) -> PrintableProj:
    """Create printable object from Proj."""
    formatted_branches = []
    bare = "b" if proj.git and proj.git.is_bare else " "
    if proj.git:
        branches = proj.git.worktrees or proj.git.branches
        for b in branches:
            if b == proj.git.active_branch:
                b_str = f"(*{b})"
                if config.is_win32():
                    b_str = f"{BCColors.GREEN_FG}{b_str}{BCColors.ENDC}"
            else:
                b_str = f"({b})"
            formatted_branches.append(b_str)
        remote_branches = [
            f"{BCColors.RED_FG}[{b}]{BCColors.ENDC}" for b in proj.git.remote_branches
        ]

    return PrintableProj(
        short=proj.short,
        name=proj.name,
        bare=bare,
        branches=formatted_branches,
        remote_branches=remote_branches,
    )


def print_project(printable: PrintableProj, all_flag: bool = False) -> None:
    """Print project formatted info."""
    name = printable.name
    max_name = 40
    if len(name) > max_name:
        name = name[:max_name] + ".."
    end = "\n" if not all_flag else " "
    print(
        "{short:<} | {name:<} {bare}: {branches}".format(
            short=printable.short,
            name=name,
            bare=printable.bare,
            branches=" ".join(printable.branches),
        ),
        end=end,
    )
    if all_flag:
        print(
            "r: {remote_branches}".format(
                remote_branches=" ".join(printable.remote_branches),
            ),
            end="\n",
        )


def print_table_headers(table: Table) -> None:
    """Print headers of a Table."""
    if not table.headers:
        return
    n_columns = len(table.headers)
    column_border = table.header_border.get("column", "")
    row_width = sum(table.widths) + (n_columns + 2) * len(column_border)
    end = column_border

    if top_border := table.header_border.get("top", ""):
        print(top_border * row_width, end="\n")

    for i, (header, width) in enumerate(zip(table.headers, table.widths, strict=True), start=1):
        if i == n_columns:
            end = "\n"
        print("{header:^{width}}".format(header=header, width=width), end=end)

    if bottom_border := table.header_border.get("bottom", ""):
        print(bottom_border * row_width, end="\n")


def print_table_rows(table: Table) -> None:
    """Print rows of a Table."""
    if not table.rows:
        return
    n_columns = len(table.headers)
    column_border = table.table_border.get("column", "")
    row_width = sum(table.widths) + (n_columns + 2) * len(column_border)

    if top_border := table.table_border.get("top", ""):
        print(top_border * row_width, end="\n")

    for row in table.rows:
        end = "|"
        for i, (val, width, alignment) in enumerate(
            zip(row, table.widths, table.alignments, strict=True), start=1
        ):
            if i == n_columns:
                end = "\n"
            print(
                "{val:{alignment}{width}}".format(val=str(val), alignment=alignment, width=width),
                end=end,
            )

    if bottom_border := table.table_border.get("bottom", ""):
        print(bottom_border * row_width, end="\n")


def print_table(table: Table) -> None:
    """Print table."""
    print_table_headers(table=table)
    print_table_rows(table=table)


def print_managed(projects: ProjDict) -> None:
    """Print formatted info for the managed projects."""
    print("> Projects:\n")
    if not projects:
        print("  na")
        return
    for project in sorted(projects.values(), key=lambda p: p.short.lower()):
        printable = proj_to_printable(proj=project)
        print_project(printable=printable)


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


# def projects_to_table(projects: ProjDict) -> Table:
#     """Prepare projects as Table."""
#     widths = []
#     rows = []
#     for _, proj in projects.items():
#         proj.short
