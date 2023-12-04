"""Project configuration."""
import os
import sys
from configparser import ConfigParser
from pathlib import Path

from pm import const
from pm import db
from pm import util
from pm.typedef import AnyDict, StrDict

PROJECTS_DIR = str(os.environ["PROJECTS_DIR"])
CONFIG_FILE = Path(const.PM_DIR / "pmconf.ini")


def dirs() -> StrDict:
    """Project directories saved in the configuration."""
    return dict(_parser()["dirs"])


def ljust() -> int:
    """Text left justify configuration."""
    return int(_parser()["print"]["ljust"])


def rjust() -> int:
    """Text right justify configuration."""
    return int(_parser()["print"]["rjust"])


def _read_config() -> ConfigParser:
    if not const.PM_DIR.is_dir():
        const.PM_DIR.mkdir()
    if not CONFIG_FILE.exists():
        CONFIG_FILE.touch()

    parser = ConfigParser()
    parser.read(CONFIG_FILE)
    write = False
    if "dirs" not in parser.sections():
        _add_default_proj_dirs(parser=parser)
        write = True
    if "sett" not in parser.sections():
        _add_default_settings_section(parser=parser)
        write = True
    if "print" not in parser.sections():
        _add_default_print_section(parser=parser)
        write = True
    if write:
        with open(CONFIG_FILE, "w+", encoding="utf-8") as fp:
            parser.write(fp)
    return parser


__parser: ConfigParser | None = None


def _parser() -> ConfigParser:
    global __parser
    if __parser:
        return __parser
    __parser = _read_config()
    return __parser


def _add_default_proj_dirs(parser: ConfigParser) -> None:
    parser.add_section("dirs")
    parser["dirs"]["projects_dir"] = PROJECTS_DIR


def _add_default_settings_section(parser: ConfigParser) -> None:
    parser.add_section("sett")
    parser["sett"]["local"] = const.LOCAL_CONFIG_NAME
    parser["sett"]["db"] = db.create_db()


def _add_default_print_section(parser: ConfigParser) -> None:
    parser.add_section("print")
    parser["print"]["rjust"] = "8"
    parser["print"]["ljust"] = "25"


def get_editor() -> str:
    """Get default editor app."""
    ed = "code"
    if "win32" == sys.platform:
        ed = r"%EDITOR%"
    elif "linux" in sys.platform:
        ed = r"$EDITOR"
    editor = os.path.expandvars(ed)
    return editor


@util.timeit
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
    if not data:
        data = {"description": "Empty", "lang": "na"}
    parser = ConfigParser()
    parser.add_section("project")
    for key, val in data.items():
        parser["project"][key] = val

    with open(local_config_file, "a", encoding="utf-8") as fp:
        parser.write(fp)
