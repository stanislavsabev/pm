# migrations/backup.py
import subprocess
import boto3
from datetime import datetime, timezone
from pathlib import Path

def backup_collection(
    collection: str,
    db_name: str,
    mongo_uri: str,
    s3_bucket: str,
    migration_id: str,
    environment: str,
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{environment}/{migration_id}/{collection}_{timestamp}.json.gz"
    local_path = Path(f"/tmp/{collection}_{timestamp}.json")

    subprocess.run([
        "mongoexport",
        f"--uri={mongo_uri}",
        f"--db={db_name}",
        f"--collection={collection}",
        f"--out={local_path}",
    ], check=True)

    # Compress and upload
    compressed_path = local_path.with_suffix(".json.gz")
    subprocess.run(["gzip", str(local_path)], check=True)

    s3 = boto3.client("s3")
    s3.upload_file(str(compressed_path), s3_bucket, filename)
    compressed_path.unlink()

    print(f"Backed up {collection} → s3://{s3_bucket}/{filename}")
    return filename