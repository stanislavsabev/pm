import abc
from dataclasses import dataclass, field

from pm.typedef import AnyDict, StrList


@dataclass
class Usage:
    """Command Usage."""

    header: str
    description: StrList = field(default_factory=list)
    flags_header: str = ""
    flags: dict[str, StrList] = field(default_factory=dict)
    short: str = ""


@dataclass
class Args:
    """Command arguments."""

    cmd_name: str
    proj_name: str | None = None
    worktree: str | None = None

    cmd_flags: StrList = field(default_factory=list)


class CmdProto(abc.ABC):
    """Application command prototype."""

    usage: Usage

    @abc.abstractmethod
    def __init__(self) -> None:
        """Create command."""
        pass

    @abc.abstractmethod
    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""

    @abc.abstractmethod
    def run(self) -> None:
        """Run command."""


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

    short: str
    name: str
    path: str
    local_config: AnyDict = field(default_factory=dict)
    git: Git | None = None


ProjDict = dict[str, Proj]
