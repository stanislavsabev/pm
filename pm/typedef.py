"""Type definitions for the project."""

import typing

AnyDict = dict[str, typing.Any]
StrDict = dict[str, str]
AnyList = list[typing.Any]
StrList = list[str]
StrListDict = dict[str, list[str]]
RecordTuple = tuple[str, str | None, str | None]
