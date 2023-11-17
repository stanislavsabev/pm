"""CLI entry point."""
import logging
import os
import sys

import typer
import typing_extensions as ext

from pm import config


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


cfg = config.init()


app = typer.Typer(name="pm", add_completion=True)


def _ls():
    typer.echo("Hello from ls")


@app.callback(invoke_without_command=True)
def pm_default(
    verbose: ext.Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    if verbose:
        print("Verbose")
    _ls()


@app.command()
def ls():
    pass  # pm_default will run `_ls`
