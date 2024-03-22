"""Printing Project data."""

from pm import config
from pm.proj_man import Proj, ProjDict, get_non_managed
from pm.typedef import StrDict


# @util.timeit
def print_project(proj: Proj) -> None:
    """Print project formatted info."""
    formatted_branches = []
    branches = proj.worktrees or proj.branches

    if branches:
        for branch in branches:
            branch_str = f"(*{branch})" if branch == proj.active_branch else f"({branch})"
            formatted_branches.append(branch_str)
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
            bare="b" if proj.is_bare else " ",
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
