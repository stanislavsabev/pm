"""Database module."""

import csv
import shutil
from tempfile import NamedTemporaryFile
from typing import Iterable

from pm.const import DB_FILE, DbColumns
from pm.typedef import RecordTuple, StrList


def create_db() -> None:
    """Create database file."""
    db_file = DB_FILE
    if not db_file.exists():
        db_file.parent.mkdir(parents=True, exist_ok=True)
        db_file.touch()


def read_db() -> Iterable[StrList]:
    """Read database file."""
    if not DB_FILE.exists():
        raise FileNotFoundError(
            "Cannot find database file. Maybe you forgot to execute `pm init`?"
        )
    with DB_FILE.open("r", encoding="utf-8") as fp:
        for line in csv.reader(fp):
            if line:
                yield line


def add_record(record: RecordTuple) -> None:
    """Write record to the database file."""
    with DB_FILE.open("a", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(record)


def update_record(record: RecordTuple) -> None:
    """Update record to the database file."""
    tempfile = NamedTemporaryFile("w+t", newline="", delete=False)

    with DB_FILE.open("r", newline="", encoding="utf-8") as dbfile, tempfile:
        reader = csv.reader(dbfile, delimiter=",", quotechar='"')
        writer = csv.writer(tempfile, delimiter=",", quotechar='"')

        for row in reader:
            if row[DbColumns.name] == record[DbColumns.name]:
                row[DbColumns.datetime_opened] = str(record[DbColumns.datetime_opened])
                row[DbColumns.recent_branch] = str(record[DbColumns.recent_branch])
            writer.writerow(row)

    shutil.move(tempfile.name, DB_FILE)
