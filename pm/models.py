import dataclasses
from typing import Protocol

from pm.typedef import LStr


class ProtoCommand(Protocol):
    """Application command prototype.

    Attributes:
        usage: str, Command help
        short_usage: str, Short command help
        flags_usage: list of str, command flags help
    """

    usage: str
    short_usage: str
    flags_usage: LStr

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """

    def run(self, args: "AppArgs") -> None:
        """Run command."""


@dataclasses.dataclass
class AppArgs:
    """Application arguments."""

    flags: str | None = None
    name: str | None = None
    command: ProtoCommand | None = None
    worktree: str | None = None
