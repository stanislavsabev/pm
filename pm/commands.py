"""Commands module."""

import logging
import os
import subprocess
import sys
from pathlib import Path

from pm import config, const, db, printer, utils
from pm.models import Cmd, Flag, Proj, TCmd, Usage
from pm.proj_manager import ProjManager, add_new_proj, get_proj_manager

logger = logging.getLogger("pm")


cmd_help_flag = Flag(name="h/help", usage=Usage("Show help on this command"))


class Ls(Cmd):
    """Handler for the ls command."""

    name = "ls"
    flags = [
        Flag(
            name="a/all",
            usage=Usage(
                header="List all projects, including non-managed.",
                description=["If PROJECT, list all worktrees / branches, including remote."],
            ),
        ),
        Flag(
            name="o/sort",
            val="",
            usage=Usage(
                header="Sort managed projects",
                arg="SORT_KEY",
                description=[
                    "Sort key - sort by",
                    "  0 / 'short' - short name",
                    "  1 / 'long' - long name",
                    " -1 / 'last' - last used, default",
                ],
            ),
        ),
        Flag(name="s/short", val="", usage=Usage(header="Foo bar")),
    ]

    usage = Usage(
        header=f"{name} [FLAGS] [PROJECT [WORKTREE]]",
        description=["List projects.", "If PROJECT is defined, list worktrees / branches"],
        positional=[
            ("PROJECT", ["Optional project name"]),
            ("WORKTREE", ["Optional worktree or folder name"]),
        ],
        short="List projects / project worktrees, [-a] for all",
    )

    def __init__(self) -> None:
        """Constructor."""
        self.all_flag = False
        self.proj_name = ""
        self.worktree = ""

    def _set_flags(self) -> None:
        for flag in self.flags:
            if flag.name == "a/all":
                self.all_flag = bool(flag.val)

    def _ls_worktree(self, proj: Proj) -> None:
        """Run ls in a worktree of a project."""
        path = Path(proj.path) / proj.full / self.worktree
        if not path.is_dir():
            raise FileNotFoundError(f"Failed to find {self.worktree} in {self.proj_name}")
        ls_command = ["ls"]
        if self.all_flag:
            ls_command.append("-a")
        ls_command.append(str(path))
        logger.debug(ls_command)

        cmd = subprocess.Popen(ls_command, shell=True)
        out_, err_ = cmd.communicate()
        if out_ or err_:
            print(f"{out_=}, {err_=}")

    def _ls_proj(self, proj: Proj) -> None:
        """Run ls in a project."""
        printable = printer.proj_to_printable(proj=proj)
        if not self.all_flag:
            printable.remote_branches.clear()
        printer.print_project(printable=printable)

    def _ls_projects(self, proj_mgr: ProjManager) -> None:
        """List all projects."""
        projects = proj_mgr.get_projects()
        if not self.all_flag:
            for _, proj in projects.items():
                if proj.git:
                    proj.git.remote_branches.clear()
        print("> Projects:")
        table = printer.projects_to_table(projects=projects)
        printer.print_table(table=table)

    def _ls_non_managed(self, proj_mgr: ProjManager) -> None:
        if non_managed := proj_mgr.get_non_managed():
            printer.print_non_managed(config.dirs(), non_managed)

    def run(self) -> None:
        """Run ls command."""
        if self.positional:
            utils.set_positional(self, self.positional, ["proj_name", "worktree"])
        self._set_flags()
        proj_mgr = get_proj_manager()

        if self.proj_name:
            proj = proj_mgr.find_proj(self.proj_name)
            if not proj:
                raise ValueError(f"Project {self.proj_name} not found")
            if self.worktree:
                self._ls_worktree(proj)
            else:
                self._ls_proj(proj)
        else:
            self._ls_projects(proj_mgr=proj_mgr)
            if self.all_flag:
                self._ls_non_managed(proj_mgr=proj_mgr)


class Cd(Cmd):
    """Handler for the cd command."""

    name = "cd"
    usage = Usage(
        header=f"{name} PROJECT [WORKTREE]",
        description=["Navigate to project"],
        positional=[
            ("PROJECT", ["Project name / short name"]),
            ("WORKTREE", ["Optional worktree name, works only with bare repos"]),
        ],
        short="Navigate to project",
    )

    def __init__(self) -> None:
        self.proj_name = ""
        self.worktree = ""

    def run(self) -> None:
        """Run cd command."""
        config.get_config()
        utils.check_npositional(self.positional, mn=1, mx=2)
        utils.set_positional(self, self.positional, ["proj_name", "worktree"])
        proj_name, wt = self.proj_name, self.worktree

        proj_mgr = get_proj_manager()
        projects = proj_mgr.get_projects()

        if config.PLATFORM != config.WINDOWS:
            print(f"Command not supported on '{config.PLATFORM}'")
            return

        for _, proj in projects.items():
            if proj.short == proj_name or proj.full == proj_name:
                break
        else:
            raise ValueError(f"Cannot find project {proj}")

        path = Path(proj.path) / proj.full
        if wt:
            path = path.joinpath(wt)
        os.system(f"start wt -d {path}")


class Open(Cmd):
    """Handler for the open command."""

    name = "open"
    usage = Usage(
        header=f"{name} PROJECT [WORKTREE]",
        description=["Open project with editor"],
        positional=[
            ("PROJECT", ["Project name / short name"]),
            ("WORKTREE", ["Optional worktree name"]),
        ],
        short="Open project",
    )

    def __init__(self) -> None:
        self.proj_name = ""
        self.worktree = ""

    def run(self) -> None:
        """Run open command."""
        utils.check_npositional(self.positional, mn=1, mx=2)
        utils.set_positional(self, self.positional, ["proj_name", "worktree"])
        proj_name, wt = self.proj_name, self.worktree

        proj_mgr = get_proj_manager()
        proj = proj_mgr.find_proj(proj_name)
        if not proj:
            raise ValueError(f"Could not find project `{proj_name}`")
        path = utils.get_proj_path(config_path=proj.path, proj_name=proj.full, worktree=wt)

        editor = config.get_editor()
        cmd = subprocess.Popen([editor, path], shell=True)
        out_, err_ = cmd.communicate()
        if out_ or err_:
            print(f"{out_=}, {err_=}")


class Add(Cmd):
    """Handler for the add command."""

    name = "add"
    usage = Usage(
        header=f"{name} PROJECT [-s SHORT_NAME]",
        description=["Add managed project"],
        positional=[
            ("PROJECT", ["Project path, also used as project name.", "`.` uses current dir."]),
        ],
        short="Add managed project",
    )

    flags = [
        Flag(name="s/short", val="", usage=Usage(header="", arg="SHORT_NAME")),
    ]

    def __init__(self) -> None:
        self.proj_name: str = ""
        self.short_name: str = ""

    def _check_config(self) -> None:
        proj_mgr = get_proj_manager()
        projects = proj_mgr.get_projects()
        for name, project in projects.items():
            if project.full == self.proj_name:
                raise FileExistsError(f"Project '{name}' already exists")
            if project.short == self.short_name:
                raise NameError(f"Short name '{self.short_name}' already exists")

    def _set_flags(self) -> None:
        for flag in self.flags:
            if flag.name == "s/short":
                self.short_name = str(flag.val)

    def run(self) -> None:
        """Run add command."""
        config.get_config()
        utils.check_npositional(self.positional, mn=1, mx=1)
        utils.set_positional(self, self.positional, ["proj_name"])
        self._set_flags()
        self.proj_name, parent = utils.path_name_and_parent(self.proj_name)

        if not self.short_name:
            self.short_name = self.proj_name
        self._check_config()
        add_new_proj(name=self.proj_name, short=self.short_name, path=parent)


class Init(Cmd):
    """Handler for the init command."""

    name = "init"
    usage = Usage(
        header=f"{name}",
        description=["Init pm. Create .pm/ folder with config and db in user's home dir "],
        short="Init pm",
    )

    def run(self) -> None:
        """Run cd command."""
        config.create_config()
        db.create_db()


class Help(Cmd):
    """Handler for the help command."""

    name = "h/help"
    usage = Usage(
        header="Show this message and exit.",
    )

    def __init__(self, cmd: Cmd | None = None) -> None:
        super().__init__()
        self._cmd = cmd
        self._flag = Flag(self.name, usage=self.usage)

    def run(self) -> None:
        """Run the app help command.

        Prints the app usage .
        """
        if self._cmd:
            self._cmd_help()
        else:
            self._app_help()

    def _cmd_help(self) -> None:
        if not self._cmd:
            return
        flags = self._cmd.flags
        flags.insert(0, self._flag)
        printer.print_usage(self._cmd.usage)
        printer.print_flags(flags=flags)

    def _app_help(self) -> None:
        app_usage = Usage(
            header="pm [-h] COMMAND [FLAGS] PROJECT [WORKTREE]",
            description=[
                f"Calling `{const.APP_NAME}` without args, lists managed projects.",
            ],
        )
        printer.print_usage(app_usage)
        printer.print_commands(COMMANDS)
        flags = [Flag(name=app_flag.name, usage=app_flag.usage) for app_flag in APP_FLAGS]
        flags.insert(0, self._flag)
        printer.print_flags(flags=flags)
        sys.exit(0)


class PackageVersion(Cmd):
    """Handler for the package version command."""

    name = "V/version"
    usage = Usage(header="Show package version")

    def run(self) -> None:
        """Run the version command."""
        printer.print_version_info()


COMMANDS: list[TCmd] = [
    Ls,
    Cd,
    Open,
    Add,
    Init,
]


APP_FLAGS: list[TCmd] = [
    PackageVersion,
]


def get_command_names() -> list[str]:
    """Returns all command names."""
    return [c.name for c in COMMANDS]


def get_app_flag_names() -> list[str]:
    """Returns app flags names."""
    return [c.name for c in APP_FLAGS]


def create_app_flag_cmd(name: str) -> Cmd:
    """Returns the command for an app flag."""
    for flag in APP_FLAGS:
        if name == flag.name:
            return flag()
    raise ValueError(f"Invalid app flag name {name}")


def create_cmd(name: str) -> Cmd:
    """Returns the command for an app flag."""
    for cmd in COMMANDS:
        if name == cmd.name:
            return cmd()
    raise ValueError(f"Invalid command name {name}")
