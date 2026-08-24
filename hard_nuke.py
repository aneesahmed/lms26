import asyncio
from app.database import engine

async def hard_nuke():
    async with engine.begin() as conn:
        print("Hard nuking schema public...")
        await conn.execute(
            __import__('sqlalchemy').text("DROP SCHEMA public CASCADE;")
        )
        await conn.execute(
            __import__('sqlalchemy').text("CREATE SCHEMA public;")
        )
        await conn.execute(
            __import__('sqlalchemy').text("GRANT ALL ON SCHEMA public TO public;")
        )
    print("Schema wiped and recreated.")

if __name__ == "__main__":
    asyncio.run(hard_nuke())
