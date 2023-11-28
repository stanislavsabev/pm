import configparser
import os
import sys

from pm.typedef import StrDict

PROJECTS_DIR = os.environ["PROJECTS_DIR"]
HOME_DIR = os.path.expanduser("~")
APP_NAME = "pm"
DB_COLUMNS = "name", "short", "path"


class Sections():
    sett: str = "settings"
    dirs: str = "dirs"
    print: str = "print"

class Config:
    global_config_name: str = "pmconf.ini"
    local_config_name: str = ".proj-cfg"
    _db_file_name: str = "db.db"
    _pm_dir_name: str = ".pm"
    _sections = Sections()

    def __init__(self) -> None:
        self.parser = configparser.ConfigParser()

    @property
    def sections(self) -> list[str]:
        return self.parser.sections()

    @property
    def dirs(self) -> StrDict:
        return dict(self.parser[Config._sections.dirs])

    @property
    def pm_dir(self) -> str:
        return os.path.join(HOME_DIR, self._pm_dir_name)

    @property
    def config_file(self) -> str:
        return os.path.join(self.pm_dir, self.global_config_name)

    @property
    def db_file(self) -> str:
        return os.path.join(self.pm_dir, self._db_file_name)

    @property
    def ljust(self) -> int:
        return int(self.parser[self._sections.print]["ljust"])

    @property
    def rjust(self) -> int:
        return int(self.parser[self._sections.print]["rjust"])


_instance: Config | None = None


def _read_config() -> Config:
    cfg = Config()
    if not os.path.isdir(cfg.pm_dir):
        os.mkdir(cfg.pm_dir)
    if not os.path.isfile(cfg.config_file):
        with open(cfg.config_file, "w+", encoding="utf-8") as fp:
            pass

    cfg.parser.read(cfg.config_file)
    write = False
    if cfg._sections.dirs not in cfg.sections:
        _add_default_proj_dirs(cfg)
        write = True
    if cfg._sections.sett not in cfg.sections:
        _add_default_settings_section(cfg)
        write = True
    if cfg._sections.print not in cfg.sections:
        _add_default_print_section(cfg)
        write = True
    if cfg._sections.dirs not in cfg.sections:
        raise ValueError("Config is missing projects directories.")
    if write:
        with open(cfg.config_file, "w+", encoding="utf-8") as fp:
            cfg.parser.write(fp)
    return cfg


def get_instance() -> Config:
    global _instance
    if _instance:
        return _instance
    _instance = _read_config()
    return _instance


def _add_default_proj_dirs(cfg: Config) -> None:
    if env_var := os.environ.get("PROJECTS_DIR"):
        cfg.parser.add_section(cfg._sections.dirs)
        cfg.parser[cfg._sections.dirs]["projects_dir"] = env_var


def _add_default_settings_section(cfg: Config) -> None:
    cfg.parser.add_section(cfg._sections.sett)
    cfg.parser[cfg._sections.sett]["local"] = cfg.local_config_name
    _create_db(cfg)


def _add_default_print_section(cfg: Config) -> None:
    cfg.parser.add_section(cfg._sections.print)
    cfg.parser[cfg._sections.print]["rjust"] = 8
    cfg.parser[cfg._sections.print]["ljust"] = 25


def _create_db(cfg: Config) -> None:
    db_file = os.path.join(cfg.pm_dir, cfg._db_file_name)
    if not os.path.isfile(db_file):
        with open(db_file, "w", encoding="utf-8"):
            pass
    cfg.parser[cfg._sections.sett]["db"] = db_file


def get_editor() -> str:
    ed = "code"
    if "win32" == sys.platform:
        ed = r"%EDITOR%"
    elif "linux" in sys.platform:
        ed = r"$EDITOR"
    editor = os.path.expandvars(ed)
    return editor
