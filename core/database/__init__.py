from sqlalchemy import MetaData, func, literal, text
from core.config.globals import settings


def to_tsvector_ix(*columns):

    s = " || ' ' || ".join(columns)

    return func.to_tsvector(literal("english"), text(s))


driver = settings.DB_DRIVER

if driver == "postgres":

    from .drivers.postgres.base import BaseAsync, BaseSync, SessionAsync

    from .drivers.postgres.async_connection import engineAsync, get_async_db

    from .drivers.postgres.sync_connection import engineSync, get_sync_db
