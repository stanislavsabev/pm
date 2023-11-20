"""CLI entry point."""
import logging
import os
from typing import Any

import typer
import typing_extensions as ext

from pm import proj
from pm.config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = typer.Typer(name="pm", add_completion=True)


def _ls(cfg: Config):
    global projects
    projects = proj.read_projects(cfg)
    proj.print_projects(projects)


@app.callback(invoke_without_command=True)
def pm_default(
    verbose: ext.Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    cfg = Config.instance()
    if verbose:
        raise NotImplementedError
    _ls(cfg)


@app.command()
def ls():
    cfg = Config.instance()
    for dir_name, dir_path in cfg.dirs.items():
        paths = [x for x in os.listdir(dir_path) if os.path.isdir(x)]
        for name in paths:
            local_file = os.path.join(dir_path, name, cfg.parser[cfg.sett_section]["local"])
            if os.path.isfile(local_file):
                proj.read_local_file(local_file)
    pass  # pm_default will run `_ls`
