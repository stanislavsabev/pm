import abc
from dataclasses import dataclass, field

from pm import argparse
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


class CmdProto(abc.ABC):
    """Application command prototype."""

    name: str
    usage: Usage

    @abc.abstractmethod
    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """

    @abc.abstractmethod
    def run(self, args: argparse.Args) -> None:
        """Run command."""
