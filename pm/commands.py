"""Commands module."""

import logging
import os
import subprocess
from pathlib import Path

from pm import config, db, printer, proj_man, utils
from pm.const import SEE_h
from pm.models import ICommand, Usage
from pm.typedef import StrList

logger = logging.getLogger("pm")


class Ls(ICommand):
    """Handler for the ls command."""

    name = "ls"
    usage = Usage(
        header=f"{name} [FLAGS] [PROJECT]",
        description=["List projects.", "If PROJECT is defined, list worktrees / branches"],
        flags={
            "-a --all": [
                "List all projects, including non-managed.",
                "If PROJECT, list all worktrees / branches, including remote.",
            ]
        },
        short="List projects / project worktrees, [-a] for all",
    )

    def __init__(self) -> None:
        """Constructor."""
        self.all_flag = False
        self.proj_name = ""

    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""
        for arg in argv:
            if utils.is_help_flag(arg):
                printer.print_usage(self.usage, exit_=True)
            if arg.startswith("-"):
                if arg.lstrip("-") in "a/all".split("/"):
                    self.all_flag = True
                else:
                    raise ValueError(f"Unknown flag '{arg}'")
            else:
                if self.proj_name:
                    logger.warning(f"Too many positional arguments{SEE_h}")
                    continue
                self.proj_name = arg

    def run(self) -> None:
        """Run ls command."""
        config.get_config()
        projects = proj_man.get_projects()

        if not self.proj_name:
            # ls all projects
            printer.print_managed(projects)

            if self.all_flag:
                printer.print_non_managed(config.dirs())
        else:
            proj = proj_man.find_proj(self.proj_name)
            if not proj:
                raise ValueError(f"Project {self.proj_name} not found")

            if self.all_flag:
                raise NotImplementedError("Using -a with a PROJECT")
            printer.print_project(proj)


class Cd(ICommand):
    """Handler for the cd command."""

    name = "cd"
    usage = Usage(
        header=f"{name} PROJECT [WORKTREE]",
        description=["Navigate to project"],
        flags={
            "PROJECT": ["Project name / short name"],
            "WORKTREE": ["Optional worktree name"],
        },
        short="Navigate to project",
    )

    def __init__(self) -> None:
        self.proj_name = ""
        self.worktree = ""

    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""
        for arg in argv:
            if utils.is_help_flag(arg):
                printer.print_usage(self.usage, exit_=True)
            if arg.startswith("-"):
                raise ValueError(f"Unknown flag '{arg}'")
            else:
                if not self.proj_name:
                    self.proj_name = arg
                elif not self.worktree:
                    self.worktree = arg
                else:
                    logger.warning(f"Too many positional arguments{SEE_h}")

    def run(self) -> None:
        """Run cd command."""
        config.get_config()
        name, wt = self.proj_name, self.worktree
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


class Open(ICommand):
    """Handler for the open command."""

    name = "open"
    usage = Usage(
        header=f"{name} PROJECT [WORKTREE]",
        description=["Open project with editor"],
        flags={
            "PROJECT": ["Project name / short name"],
            "WORKTREE": ["Optional worktree name"],
        },
        short="Open project",
    )

    def __init__(self) -> None:
        self.proj_name = ""
        self.worktree = ""
        self.ls = False
        self.a = False

    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""
        for arg in argv:
            if utils.is_help_flag(arg):
                printer.print_usage(self.usage, exit_=True)
            if arg.startswith("-"):
                if arg.lstrip("-") in "ls/la".split("/"):
                    self.ls = True
                    self.a = arg.endswith("a")
                else:
                    raise ValueError(f"Unknown flag '{arg}'")
            else:
                if not self.proj_name:
                    self.proj_name = arg
                elif not self.worktree:
                    self.worktree = arg
                else:
                    logger.warning(f"Too many positional arguments{SEE_h}")
        if not self.proj_name:
            raise ValueError(f"Missing argument PROJECT{SEE_h}")

    def _run_ls(self) -> None:
        """Run ls command from Open."""
        ls = Ls()
        ls.proj_name = self.proj_name
        ls.all_flag = self.a
        ls.run()

    def run(self) -> None:
        """Run open command."""
        if self.ls:
            self._run_ls()
            return

        config.get_config()
        name, wt = self.proj_name, self.worktree

        proj = proj_man.find_proj(name)
        if not proj:
            raise FileNotFoundError(f"Could not find project `{name}`")
        path = Path(proj.path) / proj.name
        if wt:
            path = path.joinpath(wt)

        if not path.is_dir():
            raise FileNotFoundError(f"Could not find proj path `{str(path)}`")

        editor = config.get_editor()
        cmd = subprocess.Popen(f"{editor} {path}", shell=True)
        out_, err_ = cmd.communicate()
        if out_ or err_:
            print(f"{out_=}, {err_=}")


class Add(ICommand):
    """Handler for the add command."""

    name = "add"
    usage = Usage(
        header=f"{name} PROJECT [-s SHORT_NAME]",
        description=["Add managed project"],
        flags={
            "PROJECT": [
                "Project path, also used as name.",
                "`.` uses current path as project name.",
            ],
            "-s --short": ["SHORT_NAME"],
        },
        short="Add managed project",
    )
    short_name: str | None = None

    def __init__(self) -> None:
        self.proj_name: str = ""

    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""
        ndx = 0
        while ndx < len(argv):
            arg = argv[ndx]
            if utils.is_help_flag(arg):
                printer.print_usage(self.usage, exit_=True)
            if arg.startswith("-"):
                if arg.lstrip("-") in "s/short".split("/"):
                    ndx += 1
                    if not ndx < len(argv):
                        raise ValueError(f"Missing value for flag '{arg}'{SEE_h}")
                    self.short_name = argv[ndx]
                else:
                    raise ValueError(f"Unknown flag '{arg}'")
            else:
                if self.proj_name:
                    logger.warning(f"Too many positional arguments{SEE_h}")
                    continue
                self.proj_name = arg
            ndx += 1
        if not self.proj_name:
            raise ValueError(f"Missing argument PROJECT{SEE_h}")

    def run(self) -> None:
        """Run add command."""
        config.get_config()
        path = Path(self.proj_name)
        if not path.is_dir():
            raise FileNotFoundError(f"Cannot find project path '{self.proj_name}'")

        self.proj_name = path.absolute().name
        if not self.short_name:
            self.short_name = self.proj_name

        projects = proj_man.get_projects()
        for name, project in projects.items():
            if project.name == self.proj_name:
                raise FileExistsError(f"Project '{name}' already exists")
            if project.short == self.short_name:
                raise NameError(f"Short name '{self.short_name}' already exists")
        proj_man.add_new_proj(
            name=self.proj_name, short=self.short_name, path=path.absolute().parent
        )


class Init(ICommand):
    """Handler for the init command."""

    name = "init"
    usage = Usage(
        header=f"{name}",
        description=["Init pm"],
        short="Init pm",
    )

    def __init__(self) -> None:
        pass

    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""
        if not argv:
            return
        if utils.is_help_flag(argv[0]):
            printer.print_usage(self.usage, exit_=True)
        else:
            raise ValueError(f"Invalid argument '{argv[0]}'{SEE_h}")

    def run(self) -> None:
        """Run cd command."""
        config.create_config()
        db.create_db()


class AppHelp(ICommand):
    """Handler for the help command."""

    name = "app_help"
    usage = Usage(
        header="",
        description=[""],
        short="",
    )

    def __init__(self) -> None:
        pass

    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""
        if not argv:
            return
        raise ValueError(f"Invalid argument '{argv[0]}'{SEE_h}")

    def run(self) -> None:
        """Run the app help command."""
        printer.print_app_usage()


class PackageVersion(ICommand):
    """Handler for the package version command."""

    name = "--version"
    usage = Usage(
        header="--version",
        description=["Prints the package version"],
        short="Prints the package version",
    )

    def __init__(self) -> None:
        pass

    def parse_args(self, argv: StrList) -> None:
        """Parse command arguments."""
        if not argv:
            return
        raise ValueError(f"Invalid argument '{argv[0]}'{SEE_h}")

    def run(self) -> None:
        """Run the version command."""
        printer.print_package_version()


COMMANDS: dict[str, type[ICommand]] = {
    "-ls": Ls,
    "-cd": Cd,
    "-open": Open,
    "-add": Add,
    "-init": Init,
    "app_help": AppHelp,
    "--version": PackageVersion,
}
