import abc
import enum
from dataclasses import dataclass, field
from typing import Iterable

from pm.typedef import AnyDict, StrDict, StrList


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
    remote_branches: StrList = field(default_factory=list)
    worktrees: StrList = field(default_factory=list)
    is_bare: bool = False


@dataclass
class Proj:
    """Project data.

    Attributes:
        short: str, short project name
        full: str, full project name
        path: str, project path
        local_config: dict, optional info from local config file
        git: Git, optional git repo info
    """

    full: str
    short: str
    path: str
    local_config: AnyDict = field(default_factory=dict)
    git: Git | None = field(default=None)


ProjDict = dict[str, Proj]


class Clr(enum.StrEnum):
    """Batch console colors."""

    GRAY_FG = "\033[90m"
    RED_FG = "\033[91m"
    GREEN_FG = "\033[92m"
    YELLOW_FG = "\033[93m"
    BLUE_FG = "\033[94m"
    MAGENTA_FG = "\033[95m"
    CYAN_FG = "\033[96m"
    WHITE_FG = "\033[97m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


@dataclass
class Table:
    """Table to print."""

    n_columns: int
    headers: StrList = field(default_factory=list)
    # {"column": "|", "top": "=", "bottom": "-"}
    header_border: StrDict = field(default_factory=dict)
    # {"column": "|", "top": "=", "bottom": "-"}
    table_border: StrDict = field(default_factory=dict)
    widths: list[int] = field(default_factory=list)
    alignments: list[str] = field(default_factory=list)
    rows: Iterable[StrList] | None = None


@dataclass
class PrintableProj:
    """Printable for a Proj."""

    short: str
    name: str
    bare: str
    branches: list[str] = field(default_factory=list)
    remote_branches: list[str] = field(default_factory=list)
