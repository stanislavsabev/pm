"""CLI entry point."""
import json
import logging
import os
from typing import Any

import typer
import typing_extensions as ext
from proj import Proj

from pm.config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = typer.Typer(name="pm", add_completion=True)


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


def _ls(cfg: Config):
    global projects
    projects = read_projects(cfg)
    app.info


@app.callback(invoke_without_command=True)
def pm_default(
    verbose: ext.Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    cfg = Config.get_cfg()
    if verbose:
        logger.info("verbose flag is not implemented / used yet ")
    _ls(cfg)


@app.command()
def ls():
    cfg = Config.get_cfg()
    for dir_name, dir_path in cfg.dirs.items():
        paths = [x for x in os.listdir(dir_path) if os.path.isdir(x)]
        for name in paths:
            local_file = os.path.join(dir_path, name, cfg.parser[cfg.sett_section]["local"])
            if os.path.isfile(local_file):
                read_local_file(local_file)
    pass  # pm_default will run `_ls`
