"""Project configuration."""

from functools import cache
import os
import sys
from configparser import ConfigParser
from pathlib import Path

from pm import const
from pm.typedef import AnyDict, StrDict

PROJECTS_DIR = str(os.environ["PROJECTS_DIR"])
CONFIG_FILE = Path(const.PM_DIR / "pmconf.ini")


WINDOWS = "Windows"
LINUX = "Linux"
MACOS = "Darwin"

PLATFORM = ""
if "win32" == sys.platform:
    PLATFORM = WINDOWS
elif "linux" in sys.platform:
    PLATFORM = LINUX
elif "Darwin" == sys.platform:
    PLATFORM = MACOS
else:
    raise EnvironmentError(f"Unsupported platform {sys.platform}")


def dirs() -> StrDict:
    """Project directories saved in the configuration."""
    return dict(get_config()["dirs"])


def ljust() -> int:
    """Text left justify configuration."""
    return int(get_config()["print"]["ljust"])


def rjust() -> int:
    """Text right justify configuration."""
    return int(get_config()["print"]["rjust"])


@cache
def get_config() -> ConfigParser:
    """Read config and return a ConfigParser."""
    parser = ConfigParser()

    if not const.PM_DIR.is_dir() or not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "Cannot find `pm` config. Maybe you forgot to execute `pm init`?"
        )
    parser.read(CONFIG_FILE)
    return parser


def create_config() -> None:
    """Create config data."""
    parser = ConfigParser()
    _add_default_proj_dirs(parser=parser)
    _add_default_settings_section(parser=parser)
    _add_default_print_section(parser=parser)

    const.PM_DIR.mkdir(exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.touch()
    with open(CONFIG_FILE, "w+", encoding="utf-8") as fp:
        parser.write(fp)


def _add_default_proj_dirs(parser: ConfigParser) -> None:
    parser.add_section("dirs")
    parser["dirs"]["projects_dir"] = PROJECTS_DIR


def _add_default_settings_section(parser: ConfigParser) -> None:
    parser.add_section("sett")
    parser["sett"]["local"] = const.LOCAL_CONFIG_NAME
    parser["sett"]["db"] = str(const.DB_FILE.absolute())


def _add_default_print_section(parser: ConfigParser) -> None:
    parser.add_section("print")
    parser["print"]["rjust"] = "8"
    parser["print"]["ljust"] = "25"


def get_editor() -> str:
    """Get default editor app."""
    ed = "code"
    if PLATFORM == WINDOWS:
        ed = r"%EDITOR%"
    else:
        ed = r"$EDITOR"
    editor = os.path.expandvars(ed)
    return editor


# @util.timeit
def read_local_config(path: Path) -> AnyDict:
    """Read local config file."""
    local_config_file = path / const.LOCAL_CONFIG_NAME
    local_config = {}

    if local_config_file.exists():
        with open(local_config_file, "r", encoding="utf-8") as fp:
            parser = ConfigParser()
            parser.read_file(fp)
            local_config = dict(parser["project"])
    return local_config


def write_local_config(path: Path, data: AnyDict | None = None) -> None:
    """Write to local config file."""
    local_config_file = path / const.LOCAL_CONFIG_NAME
    if local_config_file.exists():
        return
    if not data:
        data = {"description": "Empty", "lang": "na"}
    parser = ConfigParser()
    parser.add_section("project")
    for key, val in data.items():
        parser["project"][key] = val

    with open(local_config_file, "a", encoding="utf-8") as fp:
        parser.write(fp)
