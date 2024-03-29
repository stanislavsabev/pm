"""Project management module."""

import asyncio
import logging
import os
from functools import cache
from pathlib import Path

from git.repo.base import Repo

from pm import config, db
from pm.models import Git, Proj, ProjDict

# from pm import util
from pm.typedef import StrList, StrListDict

logger = logging.getLogger("pm")


def read_repo(path: Path) -> Git:
    """Read git repository.

    Returns:
        A Git model
    """
    repo = Repo(path)

    logger.debug(f"repo: {repo}")
    branches: StrList = [b.name for b in repo.branches]  # type: ignore
    worktrees: StrList = []
    if repo.bare:
        worktrees = [b for b in branches if (path / b).is_dir()]

    git = Git(
        active_branch=repo.active_branch.name,
        branches=branches,
        worktrees=worktrees,
        is_bare=repo.bare,
    )
    return git


# @util.timeit
async def read_proj(name: str, short: str, path: str) -> Proj:
    """Read project local config and git repo."""
    proj_path = Path(path) / name
    if not proj_path.exists():
        return Proj(
            name="<missing>",
            short="<missing>",
            path=path,
        )

    local_config = config.read_local_config(path=proj_path)
    git: Git | None = None
    try:
        git = read_repo(proj_path)
    except Exception:
        # TODO:  Check the error being raised if not a repo
        logger.info(f"Not a repo: {proj_path}")

    proj = Proj(name=name, short=short, path=path, local_config=local_config, git=git)
    return proj


# @util.timeit
def add_new_proj(name: str, short: str, path: Path) -> None:
    """Add new project with local file and save to the database."""
    config.write_local_config(path / name)
    proj_path: str | None = None if path == Path(config.PROJECTS_DIR) else str(path)
    short_name: str | None = None if name == short else short
    db.add_record(record=(name, short_name, proj_path))


# @util.timeit
async def read_managed(db_records: list[StrList]) -> ProjDict:
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
def read_non_managed() -> StrListDict:
    """Read non-managed projects directories."""
    dirs = config.dirs()
    non_managed: StrListDict = {}
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
def get_non_managed() -> StrListDict:
    """Cache function for the non-managed projects."""
    projects = read_non_managed()
    return projects


def find_proj(name: str) -> Proj | None:
    """Find project by name.

    Args:
        name: str, project to find

    Returns:
        A Proj instance or None, if not found
    """
    managed = get_projects()
    for proj in managed.values():
        if name in [proj.short, proj.name]:
            return proj
    non_managed = get_non_managed()

    dirs = config.dirs()
    for group, projects in non_managed.items():
        for proj_name in projects:
            if name == proj_name:
                path = Path(dirs[group]).joinpath(proj_name)
                proj = asyncio.run(read_proj(name, name, str(path)))
                return proj
    return None
