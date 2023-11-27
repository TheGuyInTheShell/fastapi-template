from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DEBUG = True if os.getenv("DEBUG") == "DEBUG" else False

# SQLALCHEMY 
engineAsync = create_async_engine(
    url=f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    echo = DEBUG,
)
SessionAsync = async_sessionmaker(engineAsync)


class BaseAsync(DeclarativeBase):
    pass


async def get_async_db():
    db = SessionAsync()
    try:
        yield db
    finally:
        await db.close()

BaseAsync.metadata.create_all(engineAsync)