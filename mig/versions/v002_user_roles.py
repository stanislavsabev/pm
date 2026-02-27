# migrations/versions/v002_split_user_name.py
from motor.motor_asyncio import AsyncIOMotorDatabase

MIGRATION_ID = "v002_split_user_name"
BACKUP_COLLECTIONS = ["users"]  # runner reads this before executing upgrade()
APP_VERSION = "1.2.0"   # app version this migration targets
COLLECTION = "users"

async def upgrade(db: AsyncIOMotorDatabase) -> None:
    """V1 → V2: split `name` into `first_name` / `last_name`."""
    async for doc in db[COLLECTION].find({"schema_version": 1}):
        parts = doc["name"].rsplit(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""
        await db[COLLECTION].update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "first_name": first,
                    "last_name": last,
                    "schema_version": 2,
                },
                "$unset": {"name": ""},
            },
        )

async def downgrade(db: AsyncIOMotorDatabase) -> None:
    """V2 → V1: merge names back."""
    async for doc in db[COLLECTION].find({"schema_version": 2}):
        await db[COLLECTION].update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "name": f"{doc['first_name']} {doc['last_name']}".strip(),
                    "schema_version": 1,
                },
                "$unset": {"first_name": "", "last_name": ""},
            },
        )