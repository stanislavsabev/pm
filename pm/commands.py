import os
import subprocess
from typing import Protocol, Type

from pm import app_args
from pm import config
from pm import proj_mgmt
from pm.typedef import LStr

HELP = ["-h", "--help"]
FLAGS = ["-a", "--all"]

WS4 = config.WS4
WS8 = config.WS8


class ProtoCommand(Protocol):
    usage: str
    short_usage: str
    flags_usage: LStr

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        """Parse command flag."""

    def run(self, args: app_args.AppArgs) -> None:
        """Run command."""


class Ls:
    usage: str = f"""ls [FLAGS]

{WS4}List projects"""
    short_usage: str = "List managed projects, [-a] for all"
    flags_usage: LStr = [
        "-a --all        List all projects, including from PROJECTS_DIR"
    ]
    all_flag = False

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        flag = argv[ndx]
        ndx += 1
        if flag.lstrip("-") in "a/all".split("/"):
            self.all_flag = True
        else:
            raise AttributeError(f"Unknown flag {flag} for command 'ls'")
        return ndx

    def run(self, args: app_args.AppArgs) -> None:
        del args
        projects = proj_mgmt.get_projects()
        proj_mgmt.print_managed(projects)

        if self.all_flag:
            proj_mgmt.print_non_managed(config.dirs())


class Cd:
    usage = f"""cd PROJECT [WORKTREE]

{WS4}Navigate to project

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name"""
    short_usage: str = "Navigate to project"
    flags_usage: LStr = []

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        del argv
        del ndx
        raise NotImplementedError

    def run(self, args: app_args.AppArgs) -> None:
        proj, wt = args.name, args.worktree
        print(f"cd {proj=} {wt=}")


class Open:
    usage: str = f"""[open] PROJECT [WORKTREE]

{WS4}Open project with editor

{WS4}PROJECT {WS8}Project name / short name
{WS4}WORKTREE{WS8}Optional worktree name"""
    short_usage: str = "Open project"
    flags_usage: LStr = []

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        flag = argv[ndx]
        ndx += 1
        if flag.lstrip("-") in "a/all".split("/"):
            self.all_flag = True
        else:
            raise AttributeError(f"Unknown flag {flag} for command 'ls'")
        return ndx

    def run(self, args: app_args.AppArgs) -> None:
        name, worktree = args.name, args.worktree
        if name is None:
            raise ValueError("Missing argument for `name` in command `open`")
        path = proj_mgmt.find_managed(name, worktree)
        if not path:
            path = proj_mgmt.find_non_managed(name, worktree)

        if not path or not os.path.isdir(path):
            raise ValueError(f"Could not find project path `{name}`")

        editor = config.get_editor()
        cmd = subprocess.Popen(f"{editor} {path}", shell=True)
        out_, err_ = cmd.communicate()
        if out_ or err_:
            print(f"{out_=}, {err_=}")


COMMANDS: dict[str, Type[ProtoCommand]] = {
    "ls": Ls,
    "cd": Cd,
    "open": Open,
}
