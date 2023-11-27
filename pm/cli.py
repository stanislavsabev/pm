"""CLI entry point."""
import logging
import os
import shlex
import subprocess
import sys
from typing import Optional

import typer
import typing_extensions as ext

from pm import config, proj_mgmt

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


context_settings = {
    "help_option_names": ["-h", "--help"],
    "allow_extra_args": True,
    "ignore_unknown_options": True,
}

app = typer.Typer(
    name=config.APP_NAME,
    add_completion=False,
    context_settings=context_settings,
    invoke_without_command=True,
    help=f"Calling `{config.APP_NAME}` without args will list managed projects.",
)


@app.callback("Default")
def callback(ctx: typer.Context):
    if not ctx.invoked_subcommand:
        ls(all_flag=False)


AllFlag = ext.Annotated[
    bool, typer.Option("--all", "-a", help="List all projects, including from PROJECTS_DIR")
]
ls_help = "List projects"


@app.command("ls", short_help=f"<-a> {ls_help}", help=ls_help)
def ls(all_flag: AllFlag = False):
    cfg = config.instance()
    projects = proj_mgmt.projects()
    proj_mgmt.print_projects(projects)

    if all_flag:
        proj_mgmt.print_dirs(cfg.dirs)


ProjOpt = ext.Annotated[str, typer.Argument(help="Project name")]
WtOpt = ext.Annotated[Optional[str], typer.Argument(help="Worktree name")]

cd_help = "Navigate to project / worktree"


@app.command(
    "cd",
    short_help=f"NAME <WORKTREE> {cd_help}",
    help=cd_help,
)
def cd_cmd(
    name: ProjOpt,
    worktree: WtOpt = None,
):
    if not sys.platform == "win32":
        print("Command `cd` is not implemented for non-Windows systems.")
        return

    print(f"cd: {name=}, {worktree=}")


open_help = "Open project / worktree"


@app.command("o", short_help="Alias for `open`", help=open_help)
@app.command(
    "open",
    short_help=f"NAME <WORKTREE> {open_help}",
    help=open_help,
)
def open_cmd(
    name: ProjOpt,
    worktree: WtOpt = None,
):
    managed = proj_mgmt.projects()
    for _, proj in managed.items():
        path = None
        if name in [proj.short, proj.name]:
            path = os.path.join(proj.path, proj.name)
            if worktree and worktree in proj.worktrees:
                path = os.path.join(path, worktree)
            break
    
    if not path:
        non_managed = proj_mgmt.non_managed()

        for _, proj_dict in non_managed.items():
            path = None
            for proj_name, path in proj_dict:
                if name == proj_name:
                    path = os.path.join(path, proj_name)
                    if worktree and worktree in proj.worktrees:
                        path = os.path.join(path, worktree)
                break

    if not path:
        raise ValueError(f"Could not find project `{name}`")

    if not os.path.isdir(path):
        raise FileNotFoundError(f"Cannot find path `{path}`")

    editor = config.get_editor()
    cmd = subprocess.Popen(f"{editor} {path}", shell=True)
    out_, err_ = cmd.communicate()
    if out_ or err_:
        print(f"{out_=}, {err_=}")


if __name__ == "__main__":
    app()
