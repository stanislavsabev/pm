import asyncio
import csv
import os
from dataclasses import dataclass
from time import sleep

from git.repo.base import Repo

from pm import config, util
from pm.typedef import AnyDict, LStr, LStrDict, StrDict

ProjDict = dict[str, "Proj"]
_projects: ProjDict = {}
_non_managed: LStrDict = {}


@dataclass
class Proj:
    short: str
    name: str
    path: str
    local_config: AnyDict | None
    branches: LStr
    active_branch: str
    worktrees: LStr | None
    bare: bool = False


def read_db(db_file: str) -> list[LStr]:
    with open(db_file, "r", encoding="utf-8") as fp:
        records = [row for row in csv.reader(fp)]
    tuple(records[0]) == config.DB_COLUMNS
    return records[1:]


def read_repo(path: str) -> tuple[LStr, str, bool, LStr]:
    repo = Repo(path)
    bare = repo.bare
    active_branch = repo.active_branch
    branches: LStr = [b.name for b in repo.branches]  # type: ignore
    worktrees: LStr = []
    if bare:
        worktrees = [x for x in os.listdir(path) if x in branches]
    return branches, active_branch.name, bare, worktrees


# @util.timeit
async def read_proj(path: str, short: str, name: str) -> Proj:
    loc = os.path.join(path, name)
    local_config = config.read_local_config(loc)
    branches, active_branch, bare, worktrees = read_repo(loc)
    proj = Proj(
        name=name,
        short=short,
        bare=bare,
        path=path,
        local_config=local_config,
        worktrees=worktrees,
        branches=branches,
        active_branch=active_branch,
    )
    return proj


# @util.timeit
async def read_managed() -> None:
    global _projects
    records = read_db(db_file=config.DB_FILE)
    tasks = []
    for name, short, path in records:
        if not path:
            path = config.PROJECTS_DIR
        if not short:
            short = name
        task = asyncio.create_task(read_proj(path, short, name))
        tasks.append(task)

    for task in tasks:
        _projects[name] = await task


@util.timeit
def read_non_managed() -> LStrDict:
    dirs = config.dirs()
    non_managed: LStrDict = {}
    for group, path in dirs.items():
        non_managed[group] = []
        for proj in os.listdir(path):
            if (
                os.path.isdir(os.path.join(path, proj))
                and proj not in get_projects()
            ):
                non_managed[group].append(proj)
    return non_managed


def get_projects() -> ProjDict:
    global _projects
    if not _projects:
        asyncio.run(read_managed())
    return _projects


@util.timeit
def get_non_managed() -> LStrDict:
    global _non_managed
    if not _non_managed:
        _non_managed = read_non_managed()
    return _non_managed


@util.timeit
def print_project(proj: Proj) -> None:
    formatted_branches = []
    branches = proj.worktrees or proj.branches

    if branches:
        for branch in branches:
            if branch == proj.active_branch:
                branch_str = f"(*{branch})"
            else:
                branch_str = f"({branch})"
            formatted_branches.append(branch_str)
    name = proj.name
    ljust = config.ljust()
    rjust = config.rjust()
    if len(name) > ljust:
        name = ".." + name[-ljust + 2 :]
    print(
        "{short:>{rjust}} | {name:<{ljust}} : {branches}".format(
            short=proj.short,
            rjust=rjust,
            ljust=ljust,
            name=name,
            branches=" ".join(formatted_branches),
        )
    )


@util.timeit
def print_managed(projects: ProjDict) -> None:
    print("> Projects:\n")
    for _, project in projects.items():
        print_project(project)


@util.timeit
def print_non_managed(dirs: StrDict) -> None:
    non_managed = get_non_managed()
    for group in dirs:
        projects = non_managed[group]
        print(f"\n> {group}:\n")
        ljust = config.ljust()
        i = 0
        for i in range(1, len(projects), 2):
            d1, d2 = projects[i - 1], projects[i]
            print(f"{d1:<{ljust}} | {d2}")
        if i < len(projects):
            print(f"{projects[-1]:<{ljust}} |")


def find_managed(name: str, worktree: str | None = None) -> str | None:
    managed = get_projects()
    for proj in managed.values():
        if name in [proj.short, proj.name]:
            path = os.path.join(proj.path, proj.name)
            if worktree and worktree in proj.worktrees:  # type: ignore
                path = os.path.join(path, worktree)
            return path
    return None


def find_non_managed(name: str, worktree: str | None = None) -> str | None:
    non_managed = get_non_managed()
    dirs = config.dirs()
    for group, projects in non_managed.items():
        for proj_name in projects:
            if name == proj_name:
                path = os.path.join(dirs[group], proj_name)
                if worktree and worktree in proj.worktrees:  # type: ignore
                    path = os.path.join(path, worktree)
                return path
    return None
