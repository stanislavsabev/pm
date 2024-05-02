"""Test utils.py."""

import pytest

from pm import utils

FLAG_NAMES = ["h/help", "V/version", "f/foo"]


@pytest.mark.parametrize(
    "flag, expect",
    [
        ("-h", "h/help"),
        ("--help", "h/help"),
        ("-V", "V/version"),
        ("--version", "V/version"),
        ("--foo", "f/foo"),
        ("-f", "f/foo"),
        ("-version", None),
        ("--h", None),
        ("--non_existent", None),
        ("not_a_flag", None),
    ],
)
def test_get_by_name(flag, expect):
    actual = utils.find_in_names(flag, FLAG_NAMES)
    assert actual == expect
