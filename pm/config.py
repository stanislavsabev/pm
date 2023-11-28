import configparser
import os
import sys
from pm import util

from pm.typedef import AnyDict, StrDict

PROJECTS_DIR = os.environ["PROJECTS_DIR"]
HOME_DIR = os.path.expanduser("~")
PM_DIR = os.path.join(HOME_DIR, ".pm")
APP_NAME = "pm"
DB_COLUMNS = "name", "short", "path"
LOCAL_CONFIG_NAME = ".proj-cfg"


class Sections:
    sett: str = "settings"
    dirs: str = "dirs"
    print: str = "print"


class Config:
    db_file = os.path.join(PM_DIR, "db.db")
    config_file = os.path.join(PM_DIR, "pmconf.ini")
    _sections = Sections()

    _parser = configparser.ConfigParser()

    @classmethod
    def dirs(cls) -> StrDict:
        return dict(cls._parser[cls._sections.dirs])

    @classmethod
    def ljust(cls) -> int:
        return int(cls._parser[cls._sections.print]["ljust"])

    @classmethod
    def rjust(cls) -> int:
        return int(cls._parser[cls._sections.print]["rjust"])


_instance: Config | None = None


@util.timeit
def _read_config() -> Config:
    cfg = Config()
    if not os.path.isdir(PM_DIR):
        os.mkdir(PM_DIR)
    if not os.path.isfile(Config.config_file):
        with open(Config.config_file, "w+", encoding="utf-8") as fp:
            pass

    Config.parser.read(Config.config_file)
    write = False
    if Config._sections.dirs not in Config._parser.sections():
        _add_default_proj_dirs()
        write = True
    if Config._sections.sett not in Config._parser.sections():
        _add_default_settings_section()
        write = True
    if Config._sections.print not in Config._parser.sections():
        _add_default_print_section()
        write = True
    if write:
        with open(Config.config_file, "w+", encoding="utf-8") as fp:
            Config.parser.write(fp)
    return cfg

def get_instance() -> Config:
    global _instance
    if _instance:
        return _instance
    _instance = _read_config()
    return _instance


def _add_default_proj_dirs() -> None:
    if env_var := os.environ.get("PROJECTS_DIR"):
        Config.parser.add_section(Config._sections.dirs)
        Config.parser[Config._sections.dirs]["projects_dir"] = env_var


def _add_default_settings_section() -> None:
    Config.parser.add_section(Config._sections.sett)
    Config.parser[Config._sections.sett]["local"] = LOCAL_CONFIG_NAME
    _create_db()


def _add_default_print_section() -> None:
    Config.parser.add_section(Config._sections.print)
    Config.parser[Config._sections.print]["rjust"] = 8
    Config.parser[Config._sections.print]["ljust"] = 25


def _create_db() -> None:
    if not os.path.isfile(Config.db_file):
        with open(Config.db_file, "w", encoding="utf-8"):
            pass
    Config.parser[Config._sections.sett]["db"] = Config.db_file


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
            parser = configparser.ConfigParser()
            parser.read_file(fp)
            local_config = dict(parser["project"])
    return local_config
