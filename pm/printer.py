"""Argument parsing module."""

import sys

from pm import __version__, config, utils
from pm.models import Clr, Flags, PrintableProj, Proj, ProjDict, Table, TCmd, Usage
from pm.typedef import StrDict, StrList, StrListDict


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
    formatted_branches: StrList = []
    remote_branches: StrList = []
    bare = "b" if proj.git and proj.git.is_bare else " "
    if proj.git:
        branches = proj.git.worktrees or proj.git.branches
        formatted_branches.extend(
            clr(Clr.GREEN_FG, f"*{b}") if b == proj.git.active_branch else b for b in branches
        )
        remote_branches.extend(clr(Clr.RED_FG, f"[{b}]") for b in proj.git.remote_branches)

    return PrintableProj(
        short=proj.short,
        name=proj.full,
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
        "{short:>10} | {name:<{max_name}} {bare}: {branches}".format(
            short=printable.short,
            name=name,
            max_name=max_name,
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

    column_border = table.table_border.get("column", "")
    row_width = sum(table.widths) + (table.n_columns + 2) * len(column_border)

    if top_border := table.table_border.get("top", ""):
        print(top_border * row_width, end="\n")

    for row in table.rows:
        end = column_border
        for i, (val, width, alignment) in enumerate(
            zip(row, table.widths, table.alignments, strict=True), start=1
        ):
            if i == table.n_columns:
                end = "\n"
            print(
                "{val:{alignment}{width}}".format(val=val, alignment=alignment, width=width),
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


def print_version_info() -> None:
    """Prints package version."""
    print(f"v{__version__}")


def projects_to_table(projects: ProjDict) -> Table:
    """Prepare projects as Table."""
    rows = []
    # prepare rows and calculate widths
    swidth, fwidth, brwith = 0, 0, 0
    for _, proj in projects.items():
        pproj = proj_to_printable(proj=proj)
        swidth = max(swidth, clr_str_len(proj.short))
        fwidth = max(fwidth, clr_str_len(proj.full))
        branches = pproj.branches + pproj.remote_branches
        curr_row_branches = ""
        more_branch_rows = []
        if branches:
            for chunk in utils.chunks(lst=branches, n=3):
                chunk_str = " ".join(chunk)
                brwith = max(brwith, clr_str_len(chunk_str))
                if not curr_row_branches:
                    curr_row_branches = chunk_str
                    continue
                # create empty row for current chunk
                more_branch_rows.append([" ", " ", " ", chunk_str])
        row: StrList = [
            pproj.short,
            pproj.name,
            pproj.bare,
            curr_row_branches,
        ]
        rows.append(row)
        if more_branch_rows:
            rows.extend(more_branch_rows)

    # headers = ["short", "full name", "b", "br/wt"]
    headers: StrList = []
    alignments: StrList = [">", "<", "^", "<"]
    widths: list[int] = [swidth + 2, fwidth + 2, 3, brwith + 2]
    table = Table(
        n_columns=len(alignments),
        headers=headers,
        widths=widths,
        alignments=alignments,
        # header_border={"column": "| ", "bottom": "-", "top": "-"},
        table_border={"column": "  ", "bottom": "-"},
        rows=rows,
    )
    return table


def clr(color: Clr, s: str) -> str:
    """Colored string."""
    return f"{color.value}{s}{Clr.ENDC.value}"


def clr_str_len(chunk_str: str) -> int:
    """Get str.len for colored string."""
    for clr in Clr:
        chunk_str = chunk_str.replace(clr.value, "")
    return len(chunk_str)
