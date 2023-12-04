"""Commands module."""
import dataclasses
import subprocess
from pathlib import Path
from typing import Protocol, Type

from pm import config
from pm import const
from pm import proj_mgmt
from pm.typedef import LStr

HELP = ["-h", "--help"]
FLAGS = ["-a", "--all"]

WS4 = const.WS4
WS8 = const.WS8


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
        """Parse command option."""

    def run(self, args: "AppArgs") -> None:
        """Run command."""


@dataclasses.dataclass
class AppArgs:
    """Application arguments."""

    flags: str | None = None
    name: str | None = None
    command: ProtoCommand | None = None
    worktree: str | None = None


class Ls:
    """Handler for the ls command."""

    usage: str = f"""ls [FLAGS]

{WS4}List projects"""
    short_usage: str = "List managed projects, [-a] for all"
    flags_usage: LStr = [
        "-a --all        List all projects, including from PROJECTS_DIR"
    ]
    all_flag = False

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option."""
        flag = argv[ndx]
        ndx += 1
        if flag.lstrip("-") in "a/all".split("/"):
            self.all_flag = True
        else:
            raise ValueError(f"Unknown flag {flag} for command 'ls'")
        return ndx

    def run(self, args: AppArgs) -> None:
        """Run ls command."""
        del args
        projects = proj_mgmt.get_projects()
        proj_mgmt.print_managed(projects)

        if self.all_flag:
            proj_mgmt.print_non_managed(config.dirs())


class Cd:
    """Handler for the cd command."""

    usage = f"""cd PROJECT [WORKTREE]

{WS4}Navigate to project

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name"""
    short_usage: str = "Navigate to project"
    flags_usage: LStr = []

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option."""
        del argv
        del ndx
        raise NotImplementedError

    def run(self, args: AppArgs) -> None:
        """Run cd command."""
        proj, wt = args.name, args.worktree
        print(f"cd {proj=} {wt=}")


class Open:
    """Handler for the open command."""

    usage: str = f"""[open] PROJECT [WORKTREE]

{WS4}Open project with editor

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name"""
    short_usage: str = "Open project"
    flags_usage: LStr = []

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option."""
        flag = argv[ndx]
        ndx += 1
        if flag.lstrip("-") in "a/all".split("/"):
            self.all_flag = True
        else:
            raise ValueError(f"Unknown flag {flag} for command 'ls'")
        return ndx

    def run(self, args: AppArgs) -> None:
        """Run open command."""
        name, worktree = args.name, args.worktree
        if name is None:
            raise ValueError("Missing argument for `name` in command `open`")
        path = proj_mgmt.find_managed(name, worktree)
        if not path:
            path = proj_mgmt.find_non_managed(name, worktree)

        if not path or not path.is_dir():
            raise FileNotFoundError(f"Could not find project path `{name}`")

        editor = config.get_editor()
        cmd = subprocess.Popen(f"{editor} {path}", shell=True)
        out_, err_ = cmd.communicate()
        if out_ or err_:
            print(f"{out_=}, {err_=}")


class Add:
    """Handler for the add command."""

    usage = f"""add PROJECT [-s SHORT_NAME]

{WS4}Add managed project

{WS4}[PROJECT] {WS8}Project path, also used as name"""
    short_usage: str = "Add managed project"
    flags_usage: LStr = ["-s --short        SHORT_NAME"]

    short_name: str | None = None

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option."""
        flag = argv[ndx]
        ndx += 1
        if flag.lstrip("-") in "s/short".split("/"):
            self.short_name = argv[ndx]
            ndx += 1
        else:
            raise ValueError(f"Unknown flag {flag} for command 'add'")
        return ndx

    def run(self, args: AppArgs) -> None:
        """Run add command."""
        if not args.name:
            raise ValueError("Missing argument for `project` in command `add`")
        name_arg = args.name
        if name_arg == ".":
            path = Path.cwd()
        elif Path(name_arg).is_dir():
            path = Path(name_arg)
        else:
            raise FileNotFoundError(f"Cannot find project path '{name_arg}'")

        if not self.short_name:
            self.short_name = path.name

        projects = proj_mgmt.get_projects()
        for name, project in projects.items():
            if project.name == path.name:
                raise FileExistsError(f"Project '{name}' already exists")
            if project.short == self.short_name:
                raise NameError(f"Short name '{self.short_name}' already exists")
        proj_mgmt.add_new_proj(
            name=path.name, short=self.short_name, path=path.absolute().parent
        )


COMMANDS: dict[str, Type[ProtoCommand]] = {
    "ls": Ls,
    "cd": Cd,
    "open": Open,
    "add": Add,
}
