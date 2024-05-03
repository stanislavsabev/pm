"""Project management module."""

import asyncio
import logging
import os
from functools import cache
from pathlib import Path

from git import InvalidGitRepositoryError
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
    remote_branches = [ref.name for ref in repo.refs if ref.is_remote()]  # type: ignore[attr-defined]

    git = Git(
        active_branch=repo.active_branch.name,
        branches=branches,
        remote_branches=remote_branches,
        worktrees=worktrees,
        is_bare=repo.bare,
    )
    return git


# @util.timeit
async def read_proj(name: str, path: str, short: str | None = None) -> Proj:
    """Read project local config and git repo."""
    proj_path = Path(path) / name
    if not proj_path.exists():
        return Proj(
            full="<missing>",
            short="<missing>",
            path=path,
        )

    local_config = config.read_local_config(path=proj_path)
    git: Git | None = None
    try:
        git = read_repo(proj_path)
    except InvalidGitRepositoryError:
        logger.info(f"Not a git repo: {proj_path}")
    proj = Proj(full=name, short=(short or name), path=path, local_config=local_config, git=git)
    return proj


# @util.timeit
def add_new_proj(name: str, short: str, path: str) -> None:
    """Add new project with local file and save to the database."""
    path_obj = Path(path)
    config.write_local_config(path_obj / name)
    proj_path: str | None = None if path_obj == Path(config.get_projects_dir()) else str(path_obj)
    short_name: str | None = None if name == short else short
    db.add_record(record=(name, short_name, proj_path))


class ProjManager:
    """Project manager."""

    def __init__(self, db_records: list[StrList]) -> None:
        self.db_records = db_records
        self.managed: ProjDict = {}
        self.non_managed: StrListDict = {}

    # @util.timeit
    async def read_managed(self) -> ProjDict:
        """Read managed projects from the database and each project's git repository."""
        projects = {}
        tasks = []
        for name, short, path in self.db_records:
            if not path:
                path = config.get_projects_dir()
            if not short:
                short = name
            task = asyncio.create_task(read_proj(name=name, short=short, path=path))
            tasks.append((name, task))

        for name, task in tasks:
            projects[name] = await task
        return projects

    # @util.timeit
    def read_non_managed(self) -> StrListDict:
        """Read non-managed projects directories."""
        dirs = config.dirs()
        managed = self.get_projects()
        non_managed: StrListDict = {}
        for group, path in dirs.items():
            non_managed[group] = []
            for proj in os.listdir(path):
                if os.path.isdir(os.path.join(path, proj)) and proj not in managed:
                    non_managed[group].append(proj)
        return non_managed

    def get_projects(self) -> ProjDict:
        """Cache function for the managed projects."""
        if not self.managed and self.db_records:
            self.managed = asyncio.run(self.read_managed())
        return self.managed

    # @util.timeit
    def get_non_managed(self) -> StrListDict:
        """Cache function for the non-managed projects."""
        if not self.non_managed:
            self.non_managed = self.read_non_managed()
        return self.non_managed

    def find_proj(self, name: str) -> Proj | None:
        """Find project by name.

        Args:
            name: str, project to find

        Returns:
            A Proj instance or None, if not found
        """
        # Try find managed
        managed = self.get_projects()
        for proj in managed.values():
            if name in [proj.short, proj.full]:
                return proj

        # Try find non-managed
        non_managed = self.get_non_managed()
        dirs = config.dirs()
        for group, projects in non_managed.items():
            for proj_name in projects:
                if name == proj_name:
                    proj = asyncio.run(read_proj(name=name, path=dirs[group]))
                    return proj
        return None


@cache
def get_proj_manager() -> ProjManager:
    """Creates project manager."""
    config.get_config()
    db_records = db.read_db()
    proj_man = ProjManager(db_records=db_records)
    return proj_man
