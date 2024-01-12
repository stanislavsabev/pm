"""Project management module."""
import asyncio
import dataclasses
import logging
import os
from pathlib import Path

from git.repo.base import Repo

from pm import config
from pm import db
from pm import util
from pm.typedef import AnyDict, LStr, LStrDict, StrDict

logger = logging.getLogger("pm")

ProjDict = dict[str, "Proj"]
_projects: ProjDict = {}
_non_managed: LStrDict = {}


@dataclasses.dataclass
class Proj:
    """Project data.

    Attributes:
        short: str, short name for the project
        name: str, the project name
        path: str, the project path
        local_config: dict, optional configuration data read from local file.
        branches: list with the project branches
        active_branch: str, the active branch, if defined
        worktrees: list with the project worktrees
        is_bare: bool, True if the project repository is bare.
    """

    short: str
    name: str
    path: str
    local_config: AnyDict | None
    branches: LStr
    active_branch: str
    worktrees: LStr | None
    is_bare: bool = False


def read_repo(path: Path) -> tuple[LStr, str, bool, LStr]:
    """Read git repository.

    Returns:
        A tuple with branches, active_branch, is_bare_repo and worktrees
    """
    repo = Repo(path)
    logger.debug(f"repo: {repo}")
    is_bare_repo = repo.bare
    active_branch = repo.active_branch
    branches: LStr = [b.name for b in repo.branches]  # type: ignore
    worktrees: LStr = []
    if is_bare_repo:
        worktrees = [x for x in os.listdir(path) if x in branches]
    return branches, active_branch.name, is_bare_repo, worktrees


# @util.timeit
async def read_proj(name: str, short: str, path: str) -> Proj:
    """Read project local config and git repo."""
    proj_path = Path(path) / name
    if not proj_path.exists():
        return Proj(
            name=name,
            short="<missing>",
            is_bare=False,
            path=path,
            local_config=None,
            worktrees=None,
            branches=[],
            active_branch="",
        )
    local_config = config.read_local_config(path=proj_path)
    branches, active_branch, is_bare, worktrees = read_repo(proj_path)
    proj = Proj(
        name=name,
        short=short,
        is_bare=is_bare,
        path=path,
        local_config=local_config,
        worktrees=worktrees,
        branches=branches,
        active_branch=active_branch,
    )
    return proj


# @util.timeit
def add_new_proj(name: str, short: str, path: Path) -> None:
    """Add new project with local file and save to the database."""
    config.write_local_config(path / name)
    proj_path: str | None = None if path == Path(config.PROJECTS_DIR) else str(path)
    short_name: str | None = None if name == short else short
    db.add_record(record=(name, short_name, proj_path))


@util.timeit
async def read_managed() -> None:
    """Read managed projects from the database and each project's git repository."""
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
    """Read non-managed projects directories."""
    dirs = config.dirs()
    non_managed: LStrDict = {}
    for group, path in dirs.items():
        non_managed[group] = []
        for proj in os.listdir(path):
            if os.path.isdir(os.path.join(path, proj)) and proj not in get_projects():
                non_managed[group].append(proj)
    return non_managed


def get_projects() -> ProjDict:
    """Cache function for the managed projects."""
    global _projects
    if not _projects:
        asyncio.run(read_managed())
    return _projects


@util.timeit
def get_non_managed() -> LStrDict:
    """Cache function for the non-managed projects."""
    global _non_managed
    if not _non_managed:
        _non_managed = read_non_managed()
    return _non_managed


@util.timeit
def print_project(proj: Proj) -> None:
    """Print project formatted info."""
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
        "{short:<{rjust}} | {name:<{ljust}} {bare}: {branches}".format(
            short=proj.short,
            rjust=rjust,
            ljust=ljust,
            name=name,
            bare="b" if proj.is_bare else " ",
            branches=" ".join(formatted_branches),
        )
    )


@util.timeit
def print_managed(projects: ProjDict) -> None:
    """Print formatted info for the managed projects."""
    print("> Projects:\n")
    for project in sorted(projects.values(), key=lambda p: p.short.lower()):
        print_project(project)


@util.timeit
def print_non_managed(dirs: StrDict) -> None:
    """Print formatted info for the non-managed projects."""
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
    """Find a managed project path."""
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
    """Find a non-managed project path."""
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
