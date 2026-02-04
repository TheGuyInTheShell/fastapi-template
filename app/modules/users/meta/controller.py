from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import Meta
from .schemas import (
    RQMeta,
    RSMeta,
    RSMetaList,
)

# prefix /meta
router = APIRouter()

tag = "meta"


@router.get("/id/{id}", response_model=RSMeta, status_code=200, tags=[tag])
async def get_meta(
    id: str | int, db: AsyncSession = Depends(get_async_db)
) -> RSMeta:
    try:
        result = await Meta.find_one(db, id)
        return RSMeta(
            id=result.id,
            uid=result.uid,
            # Add additional fields here
        )
    except Exception as e:
        print(e)
        raise e


@router.get("/", response_model=RSMetaList, status_code=200, tags=[tag])
async def get_metas(
    pag: Optional[int] = 1,
    ord: Literal["asc", "desc"] = "asc",
    status: Literal["deleted", "exists", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RSMetaList:
    try:
        result = await Meta.find_some(db, pag or 1, ord, status)
        mapped_result = list(map(
            lambda x: RSMeta(
                id=x.id,
                uid=x.uid,
                # Add additional fields here
            ),
            result,
        ))
        return RSMetaList(
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


@router.post("/", response_model=RSMeta, status_code=201, tags=[tag])
async def create_meta(
    meta: RQMeta, db: AsyncSession = Depends(get_async_db)
) -> RSMeta:
    try:
        result = await Meta(**meta.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete("/id/{id}", status_code=204, tags=[tag])
async def delete_meta(id: str | int, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await Meta.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put("/id/{id}", response_model=RSMeta, status_code=200, tags=[tag])
async def update_meta(
    id: str | int, meta: RQMeta, db: AsyncSession = Depends(get_async_db)
) -> RSMeta:
    try:
        result = await Meta.update(db, id, meta.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e
