"""Type definitions for the project."""

import typing

AnyDict = dict[str, typing.Any]
StrDict = dict[str, str]
LStr = list[str]
LStrDict = dict[str, list[str]]

RecordTuple = tuple[str, str | None, str | None]
