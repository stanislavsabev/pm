"""Project constants."""

from pathlib import Path

APP_NAME = "pm"


HOME_DIR = Path.home()
PM_DIR = Path(HOME_DIR / ".pm")
DB_FILE = Path(PM_DIR / "db.csv")
DB_COLUMNS = "name", "short", "path"
LOCAL_CONFIG_NAME = ".pm-cfg"


SEE_HELP = ", see -h for usage"
