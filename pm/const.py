"""Project constants."""

from datetime import datetime
from pathlib import Path

APP_NAME = "pm"


HOME_DIR = Path.home()
PM_DIR = Path(HOME_DIR / ".pm")
DB_FILE = Path(PM_DIR / "db.csv")
DB_COLUMNS = "name", "short", "path", "datetime_opened", "recent_branch"
LOCAL_CONFIG_NAME = ".pm-cfg"


SEE_HELP = ", see -h for usage"

DATE_FORMAT = "%Y%m%d %H:%M:%S"
DAY_ONE = datetime(2000, 1, 1)
