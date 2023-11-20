import json
from dataclasses import dataclass
from typing import Any

from pm.config import Config


def read_db(cfg: Config) -> dict[str, Any]:
    with open(cfg.db_file, "r", encoding="utf-8") as fp:
        return json.load(fp)


def read_projects(cfg: Config):
    res = {}
    db_records = read_db(cfg)
    for k, v in db_records.items():
        res[k] = Proj(**v)
    return res


def print_projects(projects):
    print(projects)


@dataclass
class Proj:
    short: str | None = None
    name: str | None = None
    path: str | None = None
    branches: list[str] | None = None
    worktrees: list[str] | None = None
    is_bare: bool = False


projects: dict[str, Proj] = {}


def read_local_file(local_file: str):
    pass
