"""Project constants."""

import enum
from datetime import datetime
from pathlib import Path

APP_NAME = "pm"


HOME_DIR = Path.home()
PM_DIR = Path(HOME_DIR / ".pm")
DB_FILE = Path(PM_DIR / "db.csv")


LOCAL_CONFIG_NAME = ".pm-cfg"


SEE_HELP = ", see -h for usage"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DAY_ONE = datetime(2000, 1, 1)


class DbColumns(enum.IntEnum):
    """Db Columns."""

    name = 0  # type: ignore[assignment]
    short = 1
    path = 2
    datetime_opened = 3
    recent_branch = 4
