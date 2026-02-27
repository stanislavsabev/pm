# migrations/compatibility.py
from pydantic import BaseModel

class CompatibilityEntry(BaseModel):
    app_version: str
    required_migrations: list[str]  # all migrations that must be applied
    schema_versions: dict[str, int]  # collection -> expected schema_version

COMPATIBILITY_MATRIX: list[CompatibilityEntry] = [
    CompatibilityEntry(
        app_version="1.0.0",
        required_migrations=["v001_initial_schema"],
        schema_versions={"users": 1},
    ),
    CompatibilityEntry(
        app_version="1.2.0",
        required_migrations=["v001_initial_schema", "v002_split_user_name"],
        schema_versions={"users": 2},
    ),
    CompatibilityEntry(
        app_version="1.3.0",
        required_migrations=[
            "v001_initial_schema",
            "v002_split_user_name",
            "v003_add_user_timestamps",
        ],
        schema_versions={"users": 2},  # same schema, just new docs get timestamps
    ),
]