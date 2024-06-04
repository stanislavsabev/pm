"""Database module."""

import csv
from typing import Iterable

from pm import const
from pm.typedef import RecordTuple, StrList


def create_db() -> None:
    """Create database file."""
    db_file = const.DB_FILE
    if not db_file.exists():
        db_file.parent.mkdir(parents=True, exist_ok=True)
        add_record(const.DB_COLUMNS)


def read_db() -> Iterable[StrList]:
    """Read database file."""
    if not const.DB_FILE.exists():
        raise FileNotFoundError(
            "Cannot find database file. Maybe you forgot to execute `pm init`?"
        )
    first_line = True
    with const.DB_FILE.open("r", encoding="utf-8") as fp:
        for line in csv.reader(fp):
            if first_line:
                first_line = False
                continue

            if line:
                yield line


def add_record(record: RecordTuple) -> None:
    """Write record to the database file."""
    with const.DB_FILE.open("a", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(record)
