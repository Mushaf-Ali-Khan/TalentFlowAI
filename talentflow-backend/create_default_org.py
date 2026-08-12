import asyncio
import asyncpg
import sys
import uuid
import json

async def main():
    conn = await asyncpg.connect('postgresql://user:pass@localhost:5432/talentflow')
    try:
        org_id = "00000000-0000-0000-0000-000000000000"
        await conn.execute('''
            INSERT INTO organizations (id, name, slug, clerk_org_id, plan, settings, created_at, updated_at)
            VALUES ($1, 'Default Organization', 'default-org', 'default', 'free', $2, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        ''', uuid.UUID(org_id), json.dumps({}))
        print("Default organization created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
