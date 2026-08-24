import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# We expect the user to provide this in an .env file or environment variable.
# Example Neon connection string: postgresql+asyncpg://user:password@ep-withered-snow-123456.us-east-2.aws.neon.tech/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/lms")

# Neon's pooled endpoint (PgBouncer, transaction mode) doesn't support asyncpg's
# server-side prepared statement cache, so it's disabled here. pool_pre_ping
# guards against Neon silently dropping idle connections underneath us.
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0},
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
