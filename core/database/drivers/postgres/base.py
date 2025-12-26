import asyncio
import uuid
from datetime import datetime
from functools import wraps
import json
from typing import Any, List, Literal, Self, Sequence, Set
from core.cache.lru import async_lru, sync_lru

from sqlalchemy import (
    TIMESTAMP,
    UUID,
    Boolean,
    Column,
    ColumnElement,
    Integer,
    String,
    Table,
    desc,
    func,
    select,
    text,
    update,
)

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sqlalchemy_utils import create_view, get_mapper

from sqlalchemy import MetaData

from .async_connection import SessionAsync

from .sync_connection import SessionSync


from .async_connection import engineAsync

from .sync_connection import engineSync


from .async_connection import get_async_db

from .sync_connection import get_sync_db

from core.cache import cache_db


def generate_uuid():

    return str(uuid.uuid4())


def generate_dll_view(tablename: str, is_deleted: str) -> str:

    return f"""

            CREATE OR REPLACE VIEW {tablename}_{'deleted' if is_deleted == 'true' else 'exists'} AS

            SELECT *

            FROM {tablename}

            WHERE is_deleted = {is_deleted};

            """


class VanillaBaseAsync(DeclarativeBase):
    pass


class BaseAsync(DeclarativeBase):

    uid: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
        primary_key=True,
        default=generate_uuid,
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True, nullable=False, autoincrement=True, unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.current_timestamp()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=func.now(), onupdate=func.current_timestamp()
    )

    deleted_at: Mapped[datetime] = mapped_column(nullable=True)

    is_deleted: Mapped[bool] = mapped_column(default=False)

    @classmethod
    @sync_lru(maxsize=24)
    def get_deleted(cls) -> Table:
        return cls.deleted

    @classmethod
    @sync_lru(maxsize=24)
    def get_exists(cls) -> Table:

        return cls.exists

    @classmethod
    @sync_lru(maxsize=24)
    def touple_to_dict(cls, arr: Sequence[Self]) -> List[Self]:

        mapped = get_mapper(cls)

        result = []

        for touple in arr:

            obj = cls()
            colums = mapped.columns

            for i, column in enumerate(colums):

                obj.__setattr__(column.name, touple[i])

            result.append(obj)
        return result

    async def save(self, db: AsyncSession):

        db.add(self)

        await db.commit()

        await db.refresh(self)
        return self

    @classmethod
    def create_global_views(cls):

        async def create(cls: type[Self]):

            sync_conn = SessionSync()

            sync_conn.execute(text(generate_dll_view(cls.__tablename__, "true")))

            sync_conn.execute(text(generate_dll_view(cls.__tablename__, "false")))

            sync_conn.commit()

            cls.deleted = create_view(
                name=f"{cls.__tablename__}_deleted",
                selectable=select(cls).where(cls.is_deleted == True),
                metadata=BaseAsync.metadata,
            )

            cls.exists = create_view(
                name=f"{cls.__tablename__}_exists",
                selectable=select(cls).where(cls.is_deleted == False),
                metadata=BaseAsync.metadata,
            )

            sync_conn.close()

        asyncio.ensure_future(create(cls))

    def __init_subclass__(cls) -> None:

        cls.create_global_views()

        return super().__init_subclass__()

    @classmethod
    async def delete(cls, db: AsyncSession, id: int | str):

        reg = await cls.find_one(db, id)

        if reg is None or reg.is_deleted:

            raise ValueError(f"No exists the register {cls.__tablename__}")

        is_deleted = True

        deleted_at = datetime.now()

        data = {"is_deleted": is_deleted, "deleted_at": deleted_at}

        query = (
            update(cls).where(cls.id == id).values(**data)
            if type(id) == int
            else update(cls).where(cls.uid == id).values(**data)
        )

        await db.execute(query)

        await db.commit()

        await db.refresh(reg)

        return reg

    @classmethod

    # update shouldn't be cached usually, but keeping consistency if user wanted it?

    # Actually user put it on update, which is weird. Updating should not be cached or should invalidate cache.

    # I will SKIP caching update as it's dangerous/incorrect.

    async def update(cls, db: AsyncSession, id: int | str, data: dict):

        updated_at = datetime.now()

        data.update({"updated_at": updated_at})

        reg = await cls.find_one(db, id)

        if reg is None or reg.is_deleted:

            raise ValueError(f"No exists the register in {cls.__tablename__}")

        query = (
            update(cls).where(cls.id == id).values(**data)
            if type(id) == int
            else update(cls).where(cls.uid == id).values(**data)
        )

        await db.execute(query)

        await db.commit()

        await db.refresh(reg)

        return reg

    @classmethod
    @async_lru(maxsize=24)
    async def find_one(cls, db: AsyncSession, id: str | int) -> type[Self]:

        query = (
            select(cls).where(cls.id == id)
            if type(id) == int
            else select(cls).where(cls.uid == id)
        )

        result = (await db.execute(query)).scalar_one_or_none()

        if result is None:

            raise ValueError(f"Not exists the register in {cls.__tablename__}")

        if result.is_deleted:

            raise ValueError(f"The register {cls.__tablename__} is deleted")
        return result

    @classmethod
    @async_lru(maxsize=24)
    async def find_all(
        cls,
        db: AsyncSession,
        status: Literal["deleted", "exists", "all"] = "all",
        filters: dict = dict(),
    ) -> List[Self]:

        base_query = select(cls).filter_by(**filters)

        if status == "deleted":

            base_query = cls.get_deleted().select().filter_by(**filters)

        if status == "exists":

            base_query = cls.get_exists().select().filter_by(**filters)

        result = (
            (await db.execute(base_query)).scalars().all()
            if status == "all"
            else (await db.execute(base_query)).all()
        )
        return result

    @classmethod
    @sync_lru(maxsize=24)
    def get_order_by(cls, order_by: str) -> Column:

        table = Table(cls.__tablename__, MetaData(), autoload_with=engineSync)

        return table.c.get(order_by)

    @classmethod
    @async_lru(maxsize=24)
    async def find_some(
        cls,
        db: AsyncSession,
        pag: int = 1,
        order_by: str = None,
        ord: str = "asc",
        status: Literal["deleted", "exists", "all"] = "all",
        filters: dict = {},
    ) -> List[Self]:

        # Determine the source and initial query

        if status == "deleted":

            selectable = cls.get_deleted()

            base_query = selectable.select().filter_by(**filters)

        elif status == "exists":

            selectable = cls.get_exists()

            base_query = selectable.select().filter_by(**filters)

        else:  # status == 'all'

            selectable = cls.__table__

            base_query = select(cls).filter_by(**filters)

        # Determine the order column

        order_column = None

        if order_by:

            if status == "all":

                # Try to get from model columns first, then table columns

                order_column = getattr(cls, order_by, None)

                if order_column is None:

                    order_column = selectable.c.get(order_by)

            else:

                order_column = selectable.c.get(order_by)

        # Fallback to id if no order column found

        if order_column is None:

            if status == "all":
                order_column = cls.id

            else:

                order_column = selectable.c.get("id")

                if order_column is None:
                    order_column = cls.id

        # Apply ordering

        if order_column is not None:

            if ord == "desc":

                base_query = base_query.order_by(order_column.desc())

            else:

                base_query = base_query.order_by(order_column.asc())

        # Pagination

        if pag <= 0:

            pag = 1

        query = base_query.limit(10).offset((pag - 1) * 10)

        result = await db.execute(query)

        result = result.scalars().all() if status == "all" else result.all()

        return result if status == "all" else cls.touple_to_dict(result)

    @classmethod
    async def find_by_colunm(cls, db: AsyncSession, column: str, value: Any):

        result = await db.execute(select(cls).where(getattr(cls, column) == value))
        return result

    @classmethod
    async def find_by_specification(cls, db: AsyncSession, specification: dict):

        result = await db.execute(select(cls).where(**specification))
        return result


class BaseSync(DeclarativeBase):

    uid: Mapped[str] = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        primary_key=True,
        default=UUID(),
    )

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)

    created_at: Mapped[datetime] = Column(TIMESTAMP, server_default=func.now())

    updated_at: Mapped[datetime] = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
    )

    is_deleted: Mapped[bool] = Column(Boolean, default=False)

    deleted_at: Mapped[datetime] = Column(TIMESTAMP, nullable=True)
