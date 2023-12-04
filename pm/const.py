from pathlib import Path

APP_NAME = "pm"

HOME_DIR = Path.home()
PM_DIR = Path(HOME_DIR / ".pm")
DB_FILE = Path(PM_DIR / "db.db")
DB_COLUMNS = "name", "short", "path"
LOCAL_CONFIG_NAME = ".proj-cfg"

WS8 = " " * 8
WS4 = " " * 4
