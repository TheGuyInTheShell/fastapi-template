import os
import time

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DEBUG = True if os.getenv("MODE") == "DEBUG" else False

# SQLALCHEMY 
engineAsync = None

def init_async_engine():
    global engineAsync
    while engineAsync is None:
        try:
            engineAsync = engineAsync = create_async_engine(
            url=f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            echo = DEBUG,
            )
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print('try')
            print(e)
            time.sleep(10)

init_async_engine()

SessionAsync = async_sessionmaker(engineAsync)

async def get_async_db():
    db = SessionAsync()
    try:
        yield db
    finally:
        await db.close()
