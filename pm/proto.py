from dataclasses import dataclass, field
from typing import Protocol

from pm.typedef import StrList


@dataclass
class Usage:
    """
    Attributes:
        usage: str, Command help
        short_usage: str, Short command help
        flags_usage: list of str, command flags help
    """

    full: str = ""
    short: str = ""
    flags: StrList = field(default_factory=list)


class CmdProto(Protocol):
    """Application command prototype."""

    name: str
    usage: Usage

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """

    def run(self) -> None:
        """Run command."""
