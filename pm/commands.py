"""Commands module."""

import os
import subprocess
from pathlib import Path

from pm import argparse, config, const, db, proj_man, proj_print, proto
from pm.typedef import StrList

HELP = ["-h", "--help"]
FLAGS = ["-a", "--all"]

WS4 = const.WS4
WS8 = const.WS8


class Ls(proto.CmdProto):
    """Handler for the ls command."""

    usage = proto.Usage(
        full=f"""ls [FLAGS]

{WS4}List projects""",
        short="List managed projects, [-a] for all",
        flags=["-a --all        List all projects, including from PROJECTS_DIR"],
    )

    def __init__(self, args: argparse.Args) -> None:
        """Create comand with args"""
        del args  # unused
        self.all_flag = False

    def parse_argv(self, argv: StrList, ndx: int) -> int:
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

    def run(self) -> None:
        """Run ls command."""
        config.get_config()
        projects = proj_man.get_projects()
        proj_print.print_managed(projects)

        if self.all_flag:
            proj_print.print_non_managed(config.dirs())


class Cd(proto.CmdProto):
    """Handler for the cd command."""

    usage = proto.Usage(
        full=f"""cd PROJECT [WORKTREE]

{WS4}Navigate to project

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name""",
        short="Navigate to project",
    )

    def __init__(self, args: argparse.Args) -> None:
        self.args = args

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
        del argv
        return ndx

    def run(self) -> None:
        """Run cd command."""
        config.get_config()
        name, wt = self.args.proj_name, self.args.worktree
        projects = proj_man.get_projects()

        if config.PLATFORM != config.WINDOWS:
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


class Open(proto.CmdProto):
    """Handler for the open command."""

    usage = proto.Usage(
        full=f"""[open] PROJECT [WORKTREE]

{WS4}Open project with editor

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name""",
        short="Open project",
    )

    def __init__(self, args: argparse.Args) -> None:
        self.args = args

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
        del argv
        return ndx

    def run(self) -> None:
        """Run open command."""
        config.get_config()
        name, worktree = self.args.proj_name, self.args.worktree
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


class Add(proto.CmdProto):
    """Handler for the add command."""

    usage = proto.Usage(
        full=f"""add PROJECT [-s SHORT_NAME]

{WS4}Add managed project

{WS4}[PROJECT] {WS8}Project path, also used as name""",
        short="Add managed project",
        flags=["-s --short        SHORT_NAME"],
    )

    short_name: str | None = None

    def __init__(self, args: argparse.Args) -> None:
        self.args = args

    def parse_argv(self, argv: StrList, ndx: int) -> int:
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

    def run(self) -> None:
        """Run add command."""
        config.get_config()
        if not self.args.proj_name:
            raise ValueError("Missing argument for `project` in command `add`")
        name_arg = self.args.proj_name
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
        proj_man.add_new_proj(name=path.name, short=self.short_name, path=path.absolute().parent)


class Init(proto.CmdProto):
    """Handler for the init command."""

    usage = proto.Usage(
        full=f"""init

{WS4}Init pm
""",
        short="Init pm",
    )

    def __init__(self, args: argparse.Args) -> None:
        del args  # unused

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option."""
        del argv
        del ndx
        raise NotImplementedError

    def run(self) -> None:
        """Run cd command."""
        config.create_config()
        db.create_db()


COMMANDS: dict[str, type[proto.CmdProto]] = {
    "-ls": Ls,
    "-cd": Cd,
    "-open": Open,
    "-add": Add,
    "-init": Init,
}
