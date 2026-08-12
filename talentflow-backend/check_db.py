import asyncio
from app.core.database import async_session
from sqlalchemy import text

async def main():
    async with async_session() as s:
        # Get the latest batch ID
        latest_batch = await s.execute(text("SELECT id FROM batches ORDER BY created_at DESC LIMIT 1"))
        batch_row = latest_batch.fetchone()
        batch_id = batch_row[0] if batch_row else None
        
        if not batch_id:
            print("No batches found in database.")
            return
            
        print(f"Checking details for latest Batch ID: {batch_id}\n")

        res = await s.execute(text("""
            SELECT id, original_filename, processing_status, 
                   profile::text IS NOT NULL as has_profile,
                   llm_score, total_score,
                   extraction_confidence
            FROM candidates 
            WHERE batch_id = :batch_id
            ORDER BY total_score DESC NULLS LAST
        """), {"batch_id": str(batch_id)})
        rows = res.fetchall()
        for r in rows:
            print(f"  {r.original_filename}: status={r.processing_status}, has_profile={r.has_profile}, llm={r.llm_score}, total={r.total_score}, conf={r.extraction_confidence}")
        
        # Also check the profile name
        res2 = await s.execute(text("""
            SELECT original_filename, (profile::json->>'name') as name,
                   (profile::json->>'total_years_experience') as years,
                   (profile::json->>'seniority_level') as seniority
            FROM candidates 
            WHERE batch_id = :batch_id
        """), {"batch_id": str(batch_id)})
        print("\nProfile details:")
        for r in res2.fetchall():
            print(f"  {r.original_filename}: name={r.name}, years={r.years}, seniority={r.seniority}")

asyncio.run(main())
