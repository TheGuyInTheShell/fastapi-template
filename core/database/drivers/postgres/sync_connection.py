from core.config.globals import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME
DEBUG = settings.MODE == "DEVELOPMENT"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create Database Engine
engineSync = create_engine(
    DB_URL,
    echo=DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    query_cache_size=1200,
)

SessionSync = sessionmaker(autocommit=False, autoflush=False, bind=engineSync)


def get_sync_db():
    db = scoped_session(SessionSync)
    try:
        yield db
    finally:
        db.close()
