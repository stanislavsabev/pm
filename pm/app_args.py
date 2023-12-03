from typing import Protocol

from pm.typedef import LStr


class ProtoCommand(Protocol):
    usage: str
    short_usage: str
    flags_usage: LStr

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command flag."""

    def run(self, args: "AppArgs") -> None:
        """Run command."""


class AppArgs:
    flags: str | None = None
    command: ProtoCommand
    name: str | None = None
    worktree: str | None = None
