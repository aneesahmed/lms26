import asyncio
from app.database import engine, Base
from app.models.org import Org
from app.models.identity import Person
from app.models.admission import AdmissionApplication

async def init():
    async with engine.begin() as conn:
        print("Dropping tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully on Neon DB!")

if __name__ == "__main__":
    asyncio.run(init())
