import pytest

from pm import argparser
from pm import commands as cmds


@pytest.mark.parametrize(
    "cli, expect_cmd, expect_argv",
    [
        ("pm", cmds.Ls, []),
        ("pm -ls", cmds.Ls, []),
        ("pm -ls -a", cmds.Ls, ["-a"]),
        ("pm -open proj_name", cmds.Open, ["proj_name"]),
        ("pm proj_name", cmds.Open, ["proj_name"]),
        ("pm proj_name -flags", cmds.Open, ["proj_name", "-flags"]),
        ("pm proj_name worktree", cmds.Open, ["proj_name", "worktree"]),
        ("pm -init", cmds.Init, []),
        ("pm -add . -s short", cmds.Add, [".", "-s", "short"]),
        ("pm -cd proj_name", cmds.Cd, ["proj_name"]),
    ],
)
def test_parse_cmd(cli, expect_cmd, expect_argv):
    sys_argv = cli.split()
    actual_cmd, actual_argv = argparser.parse_cmd(sys_argv[1:])

    assert actual_cmd == expect_cmd
    assert actual_argv == expect_argv
