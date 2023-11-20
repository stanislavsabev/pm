import configparser
import os
from dataclasses import dataclass

from pm.config import Config


@dataclass
class Proj:
    short: str | None
    name: str | None
    path: str | None
    branches: list[str] | None
    worktrees: list[str] | None
    bare: bool = False


projects: dict[str, Proj] = {}


def read_db(db_file: str) -> list[str]:
    with open(db_file, "r", encoding="utf-8") as fp:
        for line in fp:
            yield line.strip("\n")


def read_worktrees(path: str) -> list[str]:
    return []


def read_branches(path: str) -> list[str]:
    return []


def load_proj(path, cfg_file: str) -> Proj:
    with open(os.path.join(path, cfg_file), "r", encoding="utf-8") as fp:
        parser = configparser.ConfigParser()
        parser.read_file(fp)
    project = parser["project"]
    bare = project.getboolean("bare", fallback=False)
    name = project.get("name")
    short = project.get("short")
    if bare:
        worktrees = read_worktrees(path)
    branches = read_branches(path)
    return Proj(
        name=name,
        short=short,
        bare=bare,
        path=path,
        worktrees=worktrees,
        branches=branches,
    )


def read_projects(cfg: Config) -> list[Proj]:
    res = []
    for path in read_db(db_file=cfg.db_file):
        project = load_proj(path=path, cfg_file=cfg.local_config_name)
        res.append(project)
    return res


def print_projects(projects):
    for project in projects:
        print(project)
