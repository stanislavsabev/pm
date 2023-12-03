import enum
import sys
from pathlib import Path
from typing import Optional, Protocol

from pm import config
from pm.args import Args, ProtoCommand
from pm.typedef import LStr

HELP = ["-h", "--help"]
FLAGS = ["-a", "--all"]


class Ls:
    all_flag = False

    def get_flags(self):
        """print_flags"""
        return f"all_flag={self.all_flag}"

    def parse_flag(self, argv: LStr, ndx: int):
        """Parse command flag."""

    def print_usage(self):
        """Print command usage."""
        print(
            """"List projects
    -a --all    List all projects, including from PROJECTS_DIR"""
        )

    def parse_flag(self, argv: LStr, ndx: int) -> int:
        flag = argv[ndx]
        if flag.rstrip("-") in "a/all".split("/"):
            print("ls -a")
            self.all_flag = True
        else:
            raise AttributeError(f"Unknown flag {flag} for command 'ls'")
        return ndx

    def run(self, args: Args):
        print("ls")


class Cd:
    def get_flags(self):
        """print_flags"""
        return "<no flags>"

    def print_usage(self):
        """Print command usage."""
        print("cd help")

    def parse_flag(self, argv: LStr, ndx: int):
        pass

    def run(args: Args):
        proj, wt = args.project, args.worktree
        print(f"cd {proj=} {wt=}")


COMMANDS: dict[str, ProtoCommand] = {"ls": Ls, "cd": Cd}
