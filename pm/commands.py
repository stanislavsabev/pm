"""Commands module."""

import os
import subprocess
import sys
from pathlib import Path

from pm import argparse, config, const, db, proj_man, proj_print, proto
from pm.typedef import StrList

HELP = ["-h", "--help"]
FLAGS = ["-a", "--all"]

WS4 = const.WS4
WS8 = const.WS8


class Ls(proto.CmdProto):
    """Handler for the ls command."""

    name = "-ls"
    usage = proto.Usage(
        full=f"""ls [FLAGS]

{WS4}List projects""",
        short="List managed projects, [-a] for all",
        flags=["-a --all        List all projects, including from PROJECTS_DIR"],
    )

    all_flag = False

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

    def run(self, args: argparse.Args) -> None:
        """Run ls command."""
        del args
        config.get_config()
        projects = proj_man.get_projects()
        proj_print.print_managed(projects)

        if self.all_flag:
            proj_print.print_non_managed(config.dirs())


class Cd(proto.CmdProto):
    """Handler for the cd command."""

    name = "-cd"
    usage = proto.Usage(
        full=f"""cd PROJECT [WORKTREE]

{WS4}Navigate to project

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name""",
        short="Navigate to project",
    )

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
        del argv
        return ndx

    def run(self, args: argparse.Args) -> None:
        """Run cd command."""
        config.get_config()
        name, wt = args.proj_name, args.worktree
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

    name = "-open"

    usage = proto.Usage(
        full=f"""[open] PROJECT [WORKTREE]

{WS4}Open project with editor

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name""",
        short="Open project",
    )

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option.

        Returns:
            An int, last index that was parsed.
        """
        del argv
        return ndx

    def run(self, args: argparse.Args) -> None:
        """Run open command."""
        config.get_config()
        name, worktree = args.proj_name, args.worktree
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

    name = "-add"
    usage = proto.Usage(
        full=f"""add PROJECT [-s SHORT_NAME]

{WS4}Add managed project

{WS4}[PROJECT] {WS8}Project path, also used as name""",
        short="Add managed project",
        flags=["-s --short        SHORT_NAME"],
    )

    short_name: str | None = None

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

    def run(self, args: argparse.Args) -> None:
        """Run add command."""
        config.get_config()
        if not args.proj_name:
            raise ValueError("Missing argument for `project` in command `add`")
        name_arg = args.proj_name
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

    name = "-init"
    usage = proto.Usage(
        full=f"""init

{WS4}Init pm
""",
        short="Init pm",
    )

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option."""
        del argv
        del ndx
        raise NotImplementedError

    def run(self, args: argparse.Args) -> None:
        """Run cd command."""
        del args
        config.create_config()
        db.create_db()


class UnknownCommand(proto.CmdProto):
    """Handler for the init command."""

    name = "UnknownCommand"
    usage = proto.Usage(full="Unknown command")

    def parse_argv(self, argv: StrList, ndx: int) -> int:
        """Parse command option."""
        del argv
        del ndx
        raise NotImplementedError

    def run(self, args: argparse.Args) -> None:
        """Run cd command."""
        del args
        print(self.usage)
        sys.exit(1)


COMMANDS: dict[str, type[proto.CmdProto]] = {cmd.name: cmd for cmd in [Ls, Cd, Open, Add, Init]}
