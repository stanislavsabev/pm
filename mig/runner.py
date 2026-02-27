# migrations/runner.py
import importlib
from pathlib import Path
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from mig.backup import backup_collection

MIGRATIONS_COLLECTION = "_migrations"

async def get_applied(db: AsyncIOMotorDatabase) -> set[str]:
    cursor = db[MIGRATIONS_COLLECTION].find({}, {"migration_id": 1})
    return {doc["migration_id"] async for doc in cursor}

async def record_applied(db: AsyncIOMotorDatabase, migration_id: str, direction: str) -> None:
    await db[MIGRATIONS_COLLECTION].update_one(
        {"migration_id": migration_id},
        {"$set": {
            "migration_id": migration_id,
            "direction": direction,
            "applied_at": datetime.now(timezone.utc),
        }},
        upsert=True,
    )

def load_migration_modules() -> list:
    versions_dir = Path(__file__).parent / "versions"
    modules = []
    for path in sorted(versions_dir.glob("v*.py")):
        module_name = f"migrations.versions.{path.stem}"
        modules.append(importlib.import_module(module_name))
    return modules

async def upgrade_all(db: AsyncIOMotorDatabase) -> None:
    applied = await get_applied(db)
    for mod in load_migration_modules():
        if mod.MIGRATION_ID not in applied:
            print(f"Applying {mod.MIGRATION_ID}...")
            await mod.upgrade(db)
            await record_applied(db, mod.MIGRATION_ID, "upgrade")
            print(f"Done.")

async def upgrade_all_bakcup(db, environment: str, s3_bucket: str | None = None) -> None:
    applied = await get_applied(db)
    for mod in load_migration_modules():
        if mod.MIGRATION_ID not in applied:
            if s3_bucket and hasattr(mod, "BACKUP_COLLECTIONS"):
                for col in mod.BACKUP_COLLECTIONS:
                    backup_collection(col, db.name, mongo_uri, s3_bucket, mod.MIGRATION_ID, environment)
            await mod.upgrade(db)
            await record_applied(db, mod.MIGRATION_ID, "upgrade")

async def downgrade_one(db: AsyncIOMotorDatabase) -> None:
    """Roll back the most recently applied migration."""
    applied = await get_applied(db)
    modules = load_migration_modules()
    for mod in reversed(modules):
        if mod.MIGRATION_ID in applied:
            print(f"Reverting {mod.MIGRATION_ID}...")
            await mod.downgrade(db)
            await db[MIGRATIONS_COLLECTION].delete_one({"migration_id": mod.MIGRATION_ID})
            print(f"Done.")
            return