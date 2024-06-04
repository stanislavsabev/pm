"""Project management module."""

import asyncio
import logging
import os
from datetime import datetime
from functools import cache
from pathlib import Path

from git import InvalidGitRepositoryError
from git.repo.base import Repo

from pm import config, const, db
from pm.models import Git, Proj, ProjDict

# from pm import util
from pm.typedef import StrList, StrListDict

logger = logging.getLogger("pm")


async def read_repo(proj_path: Path) -> Git:
    """Read git repository.

    Returns:
        A Git model
    """
    await asyncio.sleep(0)
    repo = Repo(proj_path)
    logger.debug(f"repo: {repo}")
    branches: StrList = [b.name for b in repo.branches]  # type: ignore
    worktrees: StrList = []
    if repo.bare:
        worktrees = [b for b in branches if Path(proj_path).joinpath(b).is_dir()]
    remote_branches = [ref.name for ref in repo.refs if ref.is_remote()]  # type: ignore[attr-defined]

    git = Git(
        active_branch=repo.active_branch.name,
        branches=branches,
        remote_branches=remote_branches,
        worktrees=worktrees,
        is_bare=repo.bare,
    )
    return git


async def read_proj(record: list[str]) -> Proj:
    """Read project local config and git repo."""
    name, short, path, last_opened_str, recent_branch = record
    if not path:
        path = config.get_projects_dir()
    if not short:
        short = name
    last_opened = (
        datetime.strptime(last_opened_str, const.DATE_FORMAT) if last_opened_str else const.DAY_ONE
    )

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
        git = await read_repo(proj_path=proj_path)
    except InvalidGitRepositoryError:
        logger.info(f"Not a git repo: {proj_path}")
    return Proj(
        name=name,
        short=(short or name),
        path=path,
        local_config=local_config,
        git=git,
        last_opened=last_opened,
        recent_branch=recent_branch,
    )


def add_new_proj(name: str, short: str, path: str) -> None:
    """Add new project with local file and save to the database."""
    path_obj = Path(path)
    config.write_local_config(path_obj / name)
    proj_path = None if path_obj == Path(config.get_projects_dir()) else str(path_obj)
    short_name = None if name == short else short
    db.add_record(record=(name, short_name, proj_path, "", ""))


class ProjManager:
    """Project manager."""

    def __init__(self, managed: ProjDict) -> None:
        self.managed = managed
        self.non_managed: StrListDict = {}

    def get_managed(self) -> ProjDict:
        """Cache function for the managed projects."""
        return self.managed

    def get_non_managed(self) -> StrListDict:
        """Cache function for the non-managed projects."""
        if not self.non_managed:
            self.non_managed = asyncio.run(read_non_managed(self.managed))
        return self.non_managed

    def find_proj(self, name: str) -> Proj | None:
        """Find project by name.

        Args:
            name: str, project to find

        Returns:
            A Proj instance or None, if not found
        """
        # Try find managed
        managed = self.get_managed()
        for proj in managed.values():
            if name in [proj.short, proj.name]:
                return proj

        # Try find non-managed
        non_managed = self.get_non_managed()
        dirs = config.dirs()
        for group, projects in non_managed.items():
            for proj_name in projects:
                if name == proj_name:
                    proj = asyncio.run(read_proj(record=[name, dirs[group], "", "", ""]))
                    return proj
        return None


async def read_managed() -> ProjDict:
    """Read managed projects.

    Read managed projectsfrom the database
    and for each project read it's git repository.
    """
    projects_dict: ProjDict = {}
    tasks = []
    for db_record in db.read_db():
        task = asyncio.create_task(read_proj(record=db_record))
        tasks.append(task)

    projects_list: list[Proj] = await asyncio.gather(*tasks)
    for proj in projects_list:
        projects_dict[proj.name] = proj
    return projects_dict


async def read_non_managed(managed: ProjDict) -> StrListDict:
    """Read non-managed projects directories."""
    dirs = config.dirs()

    non_managed: StrListDict = {}
    for group, path in dirs.items():
        non_managed[group] = []
        for name in os.listdir(path):
            if name not in managed and os.path.isdir(os.path.join(path, name)):
                non_managed[group].append(name)
    return non_managed


@cache
def get_proj_manager() -> ProjManager:
    """Creates project manager."""
    config.get_config()
    managed = asyncio.run(read_managed(), debug=True)
    proj_man = ProjManager(managed=managed)
    return proj_man
