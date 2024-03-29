"""Commands module."""
import dataclasses
import os
import subprocess
from pathlib import Path
from typing import Protocol, Type

from pm import config, db
from pm import const
from pm import proj_man
from pm import proj_print
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
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
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
        config.get_config()
        projects = proj_man.get_projects()
        proj_print.print_managed(projects)

        if self.all_flag:
            proj_print.print_non_managed(config.dirs())


class Cd:
    """Handler for the cd command."""

    usage = f"""cd PROJECT [WORKTREE]

{WS4}Navigate to project

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name"""
    short_usage: str = "Navigate to project"
    flags_usage: LStr = []

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
        del argv
        return ndx

    def run(self, args: AppArgs) -> None:
        """Run cd command."""
        config.get_config()
        name, wt = args.name, args.worktree
        projects = proj_man.get_projects()

        if not config.PLATFORM == config.WINDOWS:
            print(f"Command not supported on '{config.PLATFORM}'")
            return

        for _, proj in projects.items():
            if proj.short == name or proj.name == name:
                break
        else:
            raise ValueError(f"Cannot find project {name}")

        path = Path(proj.path) / proj.name
        if wt:
            path = path.joinpath(wt)
        os.system(f"start wt -d {path}")


class Open:
    """Handler for the open command."""

    usage: str = f"""[open] PROJECT [WORKTREE]

{WS4}Open project with editor

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name"""
    short_usage: str = "Open project"
    flags_usage: LStr = []

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
        del argv
        return ndx

    def run(self, args: AppArgs) -> None:
        """Run open command."""
        config.get_config()
        name, worktree = args.name, args.worktree
        if name is None:
            raise ValueError("Missing argument for `name` in command `open`")
        path = proj_man.find_managed(name, worktree)
        if not path:
            path = proj_man.find_non_managed(name, worktree)

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
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
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
        config.get_config()
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

        projects = proj_man.get_projects()
        for name, project in projects.items():
            if project.name == path.name:
                raise FileExistsError(f"Project '{name}' already exists")
            if project.short == self.short_name:
                raise NameError(f"Short name '{self.short_name}' already exists")
        proj_man.add_new_proj(
            name=path.name, short=self.short_name, path=path.absolute().parent
        )


class Init:
    """Handler for the init command."""

    usage = f"""init

{WS4}Init pm
"""
    short_usage: str = "Init pm"
    flags_usage: LStr = []

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command option."""
        del argv
        del ndx
        raise NotImplementedError

    def run(self, args: AppArgs) -> None:
        """Run cd command."""
        del args
        config.create_config()
        db.create_db()


COMMANDS: dict[str, Type[ProtoCommand]] = {
    "ls": Ls,
    "cd": Cd,
    "open": Open,
    "add": Add,
    "init": Init,
}
