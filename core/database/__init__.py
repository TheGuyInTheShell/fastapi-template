from sqlalchemy import MetaData, func, literal, text
from dotenv import load_dotenv
import os

load_dotenv()



def to_tsvector_ix(*columns):

    s = " || ' ' || ".join(columns)

    return func.to_tsvector(literal("english"), text(s))



driver = os.getenv("DB_DRIVER")

if driver == "postgres":

    from .drivers.postgres.base import BaseAsync, BaseSync, SessionAsync

    from .drivers.postgres.async_connection import engineAsync, get_async_db

    from .drivers.postgres.sync_connection import engineSync, get_sync_db