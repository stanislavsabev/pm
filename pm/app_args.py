from pm import commands


class AppArgs:
    flags: str | None = None
    command: commands.ProtoCommand
    name: str | None = None
    worktree: str | None = None
