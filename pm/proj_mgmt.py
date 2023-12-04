import asyncio
import dataclasses
import os
from pathlib import Path

from git.repo.base import Repo

from pm import config
from pm import db
from pm import util
from pm.typedef import AnyDict, LStr, LStrDict, StrDict

ProjDict = dict[str, "Proj"]
_projects: ProjDict = {}
_non_managed: LStrDict = {}


@dataclasses.dataclass
class Proj:
    short: str
    name: str
    path: str
    local_config: AnyDict | None
    branches: LStr
    active_branch: str
    worktrees: LStr | None
    bare: bool = False


def read_repo(path: Path) -> tuple[LStr, str, bool, LStr]:
    repo = Repo(path)
    bare = repo.bare
    active_branch = repo.active_branch
    branches: LStr = [b.name for b in repo.branches]  # type: ignore
    worktrees: LStr = []
    if bare:
        worktrees = [x for x in os.listdir(path) if x in branches]
    return branches, active_branch.name, bare, worktrees


# @util.timeit
async def read_proj(name: str, short: str, path: str) -> Proj:
    proj_path = Path(path) / name
    local_config = config.read_local_config(path=proj_path)
    branches, active_branch, bare, worktrees = read_repo(proj_path)
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
def write_proj(name: str, short: str, path: Path) -> None:
    config.write_local_config(path / name)
    proj_path: str | None = None if path == Path(config.PROJECTS_DIR) else str(path)
    short_name: str | None = None if name == short else short
    db.add_record(record=(name, short_name, proj_path))


@util.timeit
async def read_managed() -> None:
    global _projects
    records = db.read_db()
    tasks = []
    for name, short, path in records:
        if not path:
            path = config.PROJECTS_DIR
        if not short:
            short = name
        task = asyncio.create_task(read_proj(name=name, short=short, path=path))
        tasks.append((name, task))

    for name, task in tasks:
        _projects[name] = await task


@util.timeit
def read_non_managed() -> LStrDict:
    dirs = config.dirs()
    non_managed: LStrDict = {}
    for group, path in dirs.items():
        non_managed[group] = []
        for proj in os.listdir(path):
            if os.path.isdir(os.path.join(path, proj)) and proj not in get_projects():
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
    for project in sorted(projects.values(), key=lambda p: p.name.lower()):
        print_project(project)


@util.timeit
def print_non_managed(dirs: StrDict) -> None:
    non_managed = get_non_managed()
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


def find_managed(name: str, worktree: str | None = None) -> Path | None:
    managed = get_projects()
    for proj in managed.values():
        if name in [proj.short, proj.name]:
            path = Path(proj.path) / proj.name
            if worktree:
                if worktree not in proj.worktrees:  # type: ignore
                    raise ValueError(
                        f"Cannot find worktree `{worktree}` in project `{proj.name}`"
                    )
                path = path.joinpath(worktree)
            return path
    return None


def find_non_managed(name: str, worktree: str | None = None) -> Path | None:
    non_managed = get_non_managed()
    dirs = config.dirs()
    for group, projects in non_managed.items():
        for proj_name in projects:
            if name == proj_name:
                path = Path(dirs[group]).joinpath(proj_name)
                if worktree:
                    path = path.joinpath(worktree)
                return path
    return None
