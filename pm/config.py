import configparser
import os
import sys

PROJECTS_DIR = os.environ["PROJECTS_DIR"]
HOME_DIR = os.path.expanduser("~")
APP_NAME = "pm"
DB_COLUMNS = "name", "short", "path"


class Config:
    sett_section = "settings"
    dirs_section = "dirs"
    global_config_name = "pmconf.ini"
    local_config_name = ".proj-cfg"
    _db_file_name = "db.db"
    _pm_dir_name = ".pm"
    _instance = None

    def __init__(self) -> None:
        self.parser = configparser.ConfigParser()

    @property
    def sections(self) -> list[str]:
        return self.parser.sections()

    @property
    def dirs(self) -> dict[str, str]:
        return self.parser[Config.dirs_section]

    @property
    def pm_dir(self) -> str:
        return os.path.join(HOME_DIR, self._pm_dir_name)

    @property
    def config_file(self) -> str:
        return os.path.join(self.pm_dir, self.global_config_name)

    @property
    def db_file(self) -> str:
        return os.path.join(self.pm_dir, self._db_file_name)


def instance() -> "Config":
    if Config._instance:
        return Config._instance
    cfg = Config()
    if not os.path.isdir(cfg.pm_dir):
        os.mkdir(cfg.pm_dir)
    if not os.path.isfile(cfg.config_file):
        with open(cfg.config_file, "w+", encoding="utf-8") as fp:
            pass

    cfg.parser.read(cfg.config_file)
    write = False
    if cfg.dirs_section not in cfg.sections:
        _define_proj_dirs(cfg)
        write = True
    if cfg.sett_section not in cfg.sections:
        _add_settings_section(cfg)
        write = True
    if cfg.dirs_section not in cfg.sections:
        raise ValueError("Config is missing projects directories.")
    if write:
        with open(cfg.config_file, "w+", encoding="utf-8") as fp:
            cfg.parser.write(fp)

    Config._instance = cfg
    return Config._instance


def _define_proj_dirs(cfg: Config) -> bool:
    if env_var := os.environ.get("PROJECTS_DIR"):
        cfg.parser.add_section(cfg.dirs_section)
        cfg.parser[cfg.dirs_section]["projects_dir"] = env_var


def _add_settings_section(cfg: Config) -> None:
    cfg.parser.add_section(cfg.sett_section)
    cfg.parser[cfg.sett_section]["local"] = cfg.local_config_name
    _create_db(cfg)


def _create_db(cfg: Config):
    db_file = os.path.join(cfg.pm_dir, cfg._db_file_name)
    if not os.path.isfile(db_file):
        with open(db_file, "w", encoding="utf-8"):
            pass
    cfg.parser[cfg.sett_section]["db"] = db_file


def get_editor():
    ed = "code"
    if "win32" == sys.platform:
        ed = r"%EDITOR%"
    elif "linux" in sys.platform:
        ed = r"$EDITOR"
    editor = os.path.expandvars(ed)
    return editor
