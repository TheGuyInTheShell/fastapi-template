import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DEBUG = True if os.getenv("DEBUG") == "DEBUG" else False

# Create Database Engine
engineSync = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}", 
    echo=DEBUG, 
    future=True
)

SessionSync = sessionmaker(
    autocommit=False, autoflush=False, bind=engineSync
)

class BaseSync(DeclarativeBase):
    pass


def get_sync_db():
    db = scoped_session(SessionSync)
    try:
        yield db
    finally:
        db.close()