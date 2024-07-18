from sqlalchemy import MetaData, func, literal, text

from .async_connection import engineAsync, get_async_db
from .sync_connection import engineSync, get_sync_db


def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal("english"), text(s))