"""Project management module."""

import asyncio
import dataclasses
import logging
import os
from functools import cache
from pathlib import Path

from git.repo.base import Repo

from pm import config, db

# from pm import util
from pm.typedef import AnyDict, LStr, LStrDict

logger = logging.getLogger("pm")

ProjDict = dict[str, "Proj"]


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
        worktrees = [b for b in branches if (path / b).is_dir()]
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


# @util.timeit
async def read_managed(db_records: list[LStr]) -> ProjDict:
    """Read managed projects from the database and each project's git repository."""
    projects = {}
    tasks = []
    for name, short, path in db_records:
        if not path:
            path = config.PROJECTS_DIR
        if not short:
            short = name
        task = asyncio.create_task(read_proj(name=name, short=short, path=path))
        tasks.append((name, task))

    for name, task in tasks:
        projects[name] = await task
    return projects


# @util.timeit
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
    if records := db.read_db():
        return asyncio.run(read_managed(db_records=records))
    return {}


# @util.timeit
@cache
def get_non_managed() -> LStrDict:
    """Cache function for the non-managed projects."""
    projects = read_non_managed()
    return projects


def find_managed(name: str, worktree: str | None = None) -> Path | None:
    """Find a managed project path."""
    managed = get_projects()
    for proj in managed.values():
        if name in [proj.short, proj.name]:
            path = Path(proj.path) / proj.name
            if worktree:
                if worktree not in proj.worktrees:  # type: ignore
                    raise ValueError(f"Cannot find worktree `{worktree}` in project `{proj.name}`")
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
