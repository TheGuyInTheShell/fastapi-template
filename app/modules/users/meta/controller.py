from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import MetaUsers
from .schemas import (
    RQMetaUsers,
    RSMetaUsers,
    RSMetaUsersList,
)

# prefix /meta
router = APIRouter()

tag = "meta"


@router.get("/id/{id}", response_model=RSMetaUsers, status_code=200, tags=[tag])
async def get_metas_users(
    id: str | int, db: AsyncSession = Depends(get_async_db)
) -> RSMetaUsers:
    try:
        result = await MetaUsers.find_one(db, id)
        return RSMetaUsers(
            id=result.id,
            uid=result.uid,
            key=result.key,
            value=result.value,
            ref_user=result.ref_user,
        )
    except Exception as e:
        print(e)
        raise e


@router.get("/", response_model=RSMetaUsersList, status_code=200, tags=[tag])
async def get_meta_users(
    pag: Optional[int] = 1,
    ord: Literal["asc", "desc"] = "asc",
    status: Literal["deleted", "exists", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RSMetaUsersList:
    try:
        result = await MetaUsers.find_some(db, pag or 1, ord, status)
        mapped_result = list(map(
            lambda x: RSMetaUsers(
                id=x.id,
                uid=x.uid,
                key=x.key,
                value=x.value,
                ref_user=x.ref_user,
            ),
            result,
        ))
        return RSMetaUsersList(
            data=mapped_result,
            total=0,
            page=0,
            page_size=0,
            total_pages=0,
            has_next=False,
            has_prev=False,
            next_page=0,
            prev_page=0,
        )
    except Exception as e:
        print(e)
        raise e


@router.post("/", response_model=RSMetaUsers, status_code=201, tags=[tag])
async def create_meta_users(
    meta: RQMetaUsers, db: AsyncSession = Depends(get_async_db)
) -> RSMetaUsers:
    try:
        result = await MetaUsers(**meta.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete("/id/{id}", status_code=204, tags=[tag])
async def delete_meta_users(id: str | int, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await MetaUsers.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put("/id/{id}", response_model=RSMetaUsers, status_code=200, tags=[tag])
async def update_meta_users(
    id: str | int, meta: RQMetaUsers, db: AsyncSession = Depends(get_async_db)
) -> RSMetaUsers:
    try:
        result = await MetaUsers.update(db, id, meta.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e
