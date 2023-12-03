from pm.typedef import LStr
from typing import Protocol


class ProtoCommand(Protocol):
    
    def get_flags() -> str:
        """print_flags"""

    def parse_flag(self, argv: LStr, ndx: int):
        """Parse command flag."""

    def print_usage(self):
        """print command usage."""

    def run(self, args: 'Args'):
        """Run command."""

class Args:
    flags: str | None = None
    command: ProtoCommand | None = None
    project: str | None = None
    worktree: str | None = None

