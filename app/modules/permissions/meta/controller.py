from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import MetaPermissions
from .schemas import (
    RQMetaPermission,
    RSMetaPermission,
    RSMetaPermissionList,
)

# prefix /meta
router = APIRouter()

tag = "meta_permissions"


@router.get("/id/{id}", response_model=RSMetaPermission, status_code=200, tags=[tag])
async def get_meta_permission(
    id: int | str, db: AsyncSession = Depends(get_async_db)
) -> RSMetaPermission:
    try:
        result = await MetaPermissions.find_one(db, id)
        return RSMetaPermission(
            id=result.id,
            uid=result.uid,
            key=result.key,
            value=result.value,
        )
    except Exception as e:
        print(e)
        raise e


@router.get("/", response_model=RSMetaPermissionList, status_code=200, tags=[tag])
async def get_meta_permissions(
    pag: Optional[int] = 1,
    ord: Literal["asc", "desc"] = "asc",
    status: Literal["deleted", "exists", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RSMetaPermissionList:
    try:
        result = await MetaPermissions.find_some(db, pag or 1, ord, status)
        result2 = list(map(
            lambda x: RSMetaPermission(
                id=x.id,
                uid=x.uid,
                key=x.key,
                value=x.value,
            ),
            result,
        ))
        return RSMetaPermissionList(
            data=result2,
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


@router.post("/", response_model=RSMetaPermission, status_code=201, tags=[tag])
async def create_meta_permission(
    meta: RQMetaPermission, db: AsyncSession = Depends(get_async_db)
) -> RSMetaPermission:
    try:
        result = await MetaPermissions(**meta.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete("/id/{id}", status_code=204, tags=[tag])
async def delete_meta_permission(id: int | str, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await MetaPermissions.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put("/id/{id}", response_model=RSMetaPermission, status_code=200, tags=[tag])
async def update_meta_permission(
    id: int | str, meta: RQMetaPermission, db: AsyncSession = Depends(get_async_db)
) -> RSMetaPermission:
    try:
        result = await MetaPermissions.update(db, id, meta.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e
