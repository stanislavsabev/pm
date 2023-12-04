import csv

from pm import const
from pm.typedef import LStr, RecordTuple


def create_db() -> str:
    db_file = const.DB_FILE
    if not db_file.exists():
        db_file.touch()
    return str(db_file.absolute())


def read_db() -> list[LStr]:
    db_file = const.DB_FILE
    with open(db_file, "r", encoding="utf-8") as fp:
        records = list(csv.reader(fp))
    assert tuple(records[0]) == const.DB_COLUMNS
    return records[1:]


def add_record(record: RecordTuple) -> None:
    db_file = const.DB_FILE
    with open(db_file, "a", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(record)
