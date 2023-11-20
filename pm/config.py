import configparser
import os
from collections import defaultdict
from functools import lru_cache


class Config:
    sett_section = "settings"
    dirs_section = "dirs"
    _config_file = "pmconf.ini"
    _db_file = "db.json"
    _local_file = ".proj-cfg"
    _pm_dir = ".pm"
    _isinstance = None

    def __init__(self) -> None:
        self.parser = configparser.ConfigParser()

    @property
    def sections(self) -> list[str]:
        return self.parser.sections()

    @property
    def dirs(self) -> dict[str, str]:
        return self.parser[Config.dirs_section]

    @property
    @classmethod
    def pm_dir(cls) -> str:
        return os.path.join(os.path.expanduser("~"), cls._pm_dir)

    @property
    @classmethod
    def config_file(cls) -> str:
        return os.path.join(cls.pm_dir(), cls._config_file)

    @property
    @classmethod
    def db_file(cls) -> str:
        return os.path.join(cls.pm_dir(), cls._db_file)

    @staticmethod
    def get_cfg() -> "Config":
        if Config._isinstance:
            return Config._isinstance
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

        Config._isinstance = cfg
        return Config._isinstance


def _define_proj_dirs(cfg: Config) -> bool:
    if env_var := os.environ.get("PROJECTS_DIR"):
        cfg.parser.add_section(cfg.dirs_section)
        cfg.parser[cfg.dirs_section]["projects_dir"] = env_var


def _add_settings_section(cfg: Config) -> None:
    cfg.parser.add_section(cfg.sett_section)
    cfg.parser[cfg.sett_section]["local"] = cfg._local_file
    _create_db(cfg)


def _create_db(cfg: Config):
    db_file = os.path.join(cfg.pm_dir, cfg._db_file)
    if not os.path.isfile(db_file):
        with open(db_file, "w", encoding="utf-8"):
            pass
    cfg.parser[cfg.sett_section]["db"] = db_file
