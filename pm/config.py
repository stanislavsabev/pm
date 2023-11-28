from configparser import ConfigParser
import os
import sys
from pm import util

from pm.typedef import AnyDict, StrDict

PROJECTS_DIR = os.environ["PROJECTS_DIR"]
HOME_DIR = os.path.expanduser("~")
PM_DIR = os.path.join(HOME_DIR, ".pm")
DB_FILE = os.path.join(PM_DIR, "db.db")
CONFIG_FILE = os.path.join(PM_DIR, "pmconf.ini")
APP_NAME = "pm"
DB_COLUMNS = "name", "short", "path"
LOCAL_CONFIG_NAME = ".proj-cfg"


def dirs() -> StrDict:
    return dict(_parser()["dirs"])


def ljust() -> int:
    return int(_parser()["print"]["ljust"])


def rjust() -> int:
    return int(_parser()["print"]["rjust"])


@util.timeit
def _read_config() -> ConfigParser:
    if not os.path.isdir(PM_DIR):
        os.mkdir(PM_DIR)
    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "w+", encoding="utf-8") as fp:
            pass

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
    if env_var := os.environ.get("PROJECTS_DIR"):
        parser.add_section("dirs")
        parser["dirs"]["projects_dir"] = env_var


def _add_default_settings_section(parser: ConfigParser) -> None:
    parser.add_section("sett")
    parser["sett"]["local"] = LOCAL_CONFIG_NAME
    _create_db(parser=parser)


def _add_default_print_section(parser: ConfigParser) -> None:
    parser.add_section("print")
    parser["print"]["rjust"] = 8
    parser["print"]["ljust"] = 25


def _create_db(parser: ConfigParser) -> None:
    if not os.path.isfile(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8"):
            pass
    parser["sett"]["db"] = DB_FILE


def get_editor() -> str:
    ed = "code"
    if "win32" == sys.platform:
        ed = r"%EDITOR%"
    elif "linux" in sys.platform:
        ed = r"$EDITOR"
    editor = os.path.expandvars(ed)
    return editor


@util.timeit
def read_local_config(loc: str) -> AnyDict:
    local_config_file = os.path.join(loc, LOCAL_CONFIG_NAME)
    local_config = {}

    if os.path.isfile(local_config_file):
        with open(local_config_file, "r", encoding="utf-8") as fp:
            parser = ConfigParser()
            parser.read_file(fp)
            local_config = dict(parser["project"])
    return local_config
