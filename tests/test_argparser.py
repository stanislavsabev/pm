from typing import Any

import pytest

from pm import argparser, models


def isin_flags(actual: models.Flags, expect: tuple[str, Any]) -> bool:
    """Checks expected flag name and value is in the actual flags."""
    expect_name, expect_val = expect
    return any(flag.name == expect_name and flag.val == expect_val for flag in actual)


@pytest.mark.parametrize(
    "argv_str, expect_name, expect_flags, expect_positional",
    [
        ("pm", "ls", None, None),
        ("pm ls", "ls", None, None),
        ("pm ls -a", "ls", [("a/all", True)], None),
        ("pm ls --all", "ls", [("a/all", True)], None),
        ("pm open proj_name", "open", None, ["proj_name"]),
        ("pm open proj_name worktree", "open", [], ["proj_name", "worktree"]),
        ("pm init", "init", [], []),
        ("pm add . -s foo", "add", [("s/short", "foo")], ["."]),
        ("pm cd proj_name", "cd", [], ["proj_name"]),
    ],
)
def test_parse_command_args(argv_str, expect_name, expect_flags, expect_positional):
    sys_argv = argv_str.split()
    actual = argparser.parse(sys_argv[1:])

    assert actual.name == expect_name
    if expect_positional:
        assert actual.positional == expect_positional
    if expect_flags:
        for expect in expect_flags:
            assert isin_flags(actual.flags, expect)


@pytest.mark.parametrize(
    "argv_str, expect_name",
    [
        ("pm -V", "V/version"),
        ("pm --version", "V/version"),
        ("pm --help", "h/help"),
        ("pm -h", "h/help"),
    ],
)
def test_parse_app_flags(argv_str, expect_name):
    sys_argv = argv_str.split()
    actual = argparser.parse(sys_argv[1:])
    assert actual.name == expect_name


@pytest.mark.parametrize(
    "flag, argv, expect_val, expect_ndx_offset",
    [
        (
            models.Flag(name="a/all"),
            ["-a", "foo"],
            True,
            0,
        ),
        (
            models.Flag(name="s/short", val=""),
            ["-s", "foo"],
            "foo",
            1,
        ),
        (
            models.Flag(name="n/names", val=[]),
            ["--names", "foo", "bar", "--next"],
            ["foo", "bar"],
            2,
        ),
    ],
)
def test_parse_flag(flag, argv, expect_val, expect_ndx_offset):
    ndx = 0
    actual = argparser.parse_flag(flag, argv, ndx)
    assert flag.val == expect_val
    assert actual == ndx + expect_ndx_offset
