import asyncio
import asyncpg
import sys

async def main():
    conn = await asyncpg.connect('postgresql://user:pass@localhost:5432/talentflow')
    await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    await conn.close()
    print("Vector extension created successfully.")

if __name__ == '__main__':
    asyncio.run(main())
