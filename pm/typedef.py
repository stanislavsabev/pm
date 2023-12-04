import typing

import typer
import typing_extensions

Annotated = typing_extensions.Annotated

AnyDict = dict[str, typing.Any]
StrDict = dict[str, str]
LStr = list[str]
LStrDict = dict[str, list[str]]

ProjOpt = Annotated[typing.Optional[str], typer.Argument(help="Project name")]
WtOpt = Annotated[typing.Optional[str], typer.Argument(help="Worktree name")]

RecordTuple = tuple[str, str | None, str | None]
