import abc
from dataclasses import dataclass, field
from typing import Iterable

from pm.typedef import AnyDict, StrList


@dataclass
class Usage:
    """Command Usage."""

    header: str
    arg: str = field(default="")
    description: StrList = field(default_factory=list)
    positional: list[tuple[str, list[str]]] | None = field(default=None)
    flags_header: str = ""
    short: str = ""


@dataclass
class Flag:
    """Flag Definition."""

    name: str
    val: bool | str | list[str] = field(default=False)
    usage: Usage | None = field(default=None)


Flags = Iterable[Flag]


class Cmd(abc.ABC):
    """Cmd prototype."""

    name: str
    usage: Usage
    flags: list[Flag] = []
    positional: list[str] = []

    @abc.abstractmethod
    def run(self) -> None:
        """Run command."""
        pass


TCmd = type[Cmd]


@dataclass
class Git:
    """Git repo.

    Attributes:
        branches: list with the project branches
        active_branch: str, the active branch, if defined
        worktrees: list with the project worktrees
        is_bare: bool, True if the project repository is bare.
    """

    active_branch: str
    branches: StrList = field(default_factory=list)
    worktrees: StrList = field(default_factory=list)
    is_bare: bool = False


@dataclass
class Proj:
    """Project data.

    Attributes:
        short: str, short name for the project
        name: str, the project name
        path: str, the project path
        local_config: dict, optional configuration data read from local file.
    """

    name: str
    short: str
    path: str
    local_config: AnyDict = field(default_factory=dict)
    git: Git | None = field(default=None)


ProjDict = dict[str, Proj]
