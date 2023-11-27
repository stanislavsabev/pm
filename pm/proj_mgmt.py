import configparser
import csv
import os
from dataclasses import dataclass
from typing import Any

from git.repo.base import Repo

from pm import config
from pm.config import Config


@dataclass
class Proj:
    short: str | None
    name: str | None
    path: str | None
    local_config: dict[str, Any] | None
    branches: list[str] | None
    active_branch: str
    worktrees: list[str] | None
    bare: bool = False


_projects: dict[str, Proj] = {}


def read_db(db_file: str) -> list[str]:
    with open(db_file, "r", encoding="utf-8") as fp:
        records = [row for row in csv.reader(fp)]
    records[0] == config.DB_COLUMNS
    return records[1:]


def read_local_config(local_config_file) -> dict[str, Any]:
    local_config = {}

    if os.path.isfile(local_config_file):
        with open(local_config_file, "r", encoding="utf-8") as fp:
            parser = configparser.ConfigParser()
            parser.read_file(fp)
            local_config = dict(parser["project"])
    return local_config


def read_repo(path) -> Proj:
    repo = Repo(path)
    bare = repo.bare
    active_branch = repo.active_branch
    branches = [b.name for b in repo.branches]
    worktrees = []
    if bare:
        worktrees = [x for x in os.listdir(path) if x in branches]
    return branches, active_branch, bare, worktrees


def read_projects(cfg: Config) -> dict[str, Proj]:
    global _projects
    records = read_db(db_file=cfg.db_file)
    for name, short, path in records:
        if not path:
            path = config.PROJECTS_DIR
        if not short:
            short = name
        loc = os.path.join(path, name)
        local_config = read_local_config(os.path.join(loc, cfg.local_config_name))
        branches, active_branch, bare, worktrees = read_repo(loc)
        _projects[name] = Proj(
            name=name,
            short=short,
            bare=bare,
            path=path,
            local_config=local_config,
            worktrees=worktrees,
            branches=branches,
            active_branch=active_branch.name,
        )
    return _projects


def projects() -> dict[str, Proj]:
    global _projects
    if not _projects:
        _projects = read_projects(config.instance())
    return _projects


def print_project(proj: Proj):
    formatted_branches = []
    branches = proj.worktrees or proj.branches
    for branch in branches:
        if branch == proj.active_branch:
            formatted_branches.append(f"*{branch}")
        else:
            formatted_branches.append(branch)
    name = proj.name
    if len(name) > 25:
        name = ".." + name[-23:]
    print(
        "{short:>8} | {name:<25} : {branches}".format(
            short=proj.short,
            name=name,
            branches=" ".join(formatted_branches),
        )
    )


def print_projects(projects: dict[str, Proj]):
    print("> Projects:\n")
    for _, project in projects.items():
        print_project(project)


def print_dirs(dirs: dict[str, str]):
    for name, path in dirs.items():
        subdirs = [
            x
            for x in os.listdir(path)
            if os.path.isdir(os.path.join(path, x)) and x not in projects()
        ]
        print(f"\n> {name}\n")
        for i in range(1, len(subdirs), 2):
            s1, s2 = subdirs[i - 1], subdirs[i]
            print(f"{s1:<25} | {s2}")
        if i < len(subdirs):
            print(f"{subdirs[-1]:<25} |")
