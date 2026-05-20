"""
Retrigger the stuck batch: 
1. Copy CV files into the mock storage under the r2_keys used by the stuck candidates
2. Call the retry API endpoint
"""
import asyncio
import shutil
import pathlib
import urllib.request
import json

from app.core.database import async_session
from app.utils.storage import MOCK_STORAGE_ROOT
from sqlalchemy import text

# Paths to the actual CV files
CV_DIR = pathlib.Path(r"C:\Users\Tony_Stark\Professional\Startup\FYP\TalentFlowAI")

async def main():
    # 1. Find stuck candidates and their r2_keys
    async with async_session() as session:
        result = await session.execute(
            text("SELECT id, r2_key, original_filename FROM candidates WHERE processing_status = 'pending' ORDER BY created_at DESC LIMIT 10")
        )
        stuck = result.fetchall()

    print(f"Found {len(stuck)} stuck candidates:")
    for c in stuck:
        print(f"  {c.id} -> {c.r2_key} ({c.original_filename})")

        # 2. Copy the actual CV file to the mock storage path
        src = CV_DIR / c.original_filename
        if not src.exists():
            print(f"    WARNING: Source file not found: {src}")
            continue

        dest = MOCK_STORAGE_ROOT / c.r2_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest))
        print(f"    Copied to: {dest}")

    # 3. Find the batch IDs of stuck candidates and trigger retry
    async with async_session() as session:
        result = await session.execute(
            text("SELECT DISTINCT batch_id FROM candidates WHERE processing_status = 'pending'")
        )
        batch_ids = [str(row.batch_id) for row in result.fetchall()]

    for batch_id in batch_ids:
        print(f"\nTriggering retry for batch: {batch_id}")
        try:
            req = urllib.request.Request(
                f"http://localhost:8000/api/v1/pipeline/{batch_id}/retry",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=b""
            )
            resp = urllib.request.urlopen(req)
            print(f"  Response: {resp.read().decode()}")
        except Exception as e:
            print(f"  Error: {e}")

asyncio.run(main())
