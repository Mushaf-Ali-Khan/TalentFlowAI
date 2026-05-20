import asyncio
from app.core.database import async_session
from sqlalchemy import text

async def main():
    async with async_session() as s:
        res = await s.execute(text("""
            SELECT id, original_filename, processing_status, 
                   profile::text IS NOT NULL as has_profile,
                   llm_score, total_score,
                   extraction_confidence
            FROM candidates 
            WHERE batch_id = '34aba099-52e6-4de8-8467-8221c16b1d72'
            ORDER BY total_score DESC NULLS LAST
        """))
        rows = res.fetchall()
        for r in rows:
            print(f"  {r.original_filename}: status={r.processing_status}, has_profile={r.has_profile}, llm={r.llm_score}, total={r.total_score}, conf={r.extraction_confidence}")
        
        # Also check the profile name
        res2 = await s.execute(text("""
            SELECT original_filename, (profile::json->>'name') as name,
                   (profile::json->>'total_years_experience') as years,
                   (profile::json->>'seniority_level') as seniority
            FROM candidates 
            WHERE batch_id = '34aba099-52e6-4de8-8467-8221c16b1d72'
        """))
        print("\nProfile details:")
        for r in res2.fetchall():
            print(f"  {r.original_filename}: name={r.name}, years={r.years}, seniority={r.seniority}")

asyncio.run(main())
