from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import Permission
from .schemas import RQPermission, RSPermission, RSPermissionList

# prefix /permissions
router = APIRouter()
tag = 'permissions'

@router.get('/id/{id}', response_model=RSPermission, status_code=200, tags=[tag])
async def get_Permission(id: str, db: AsyncSession = Depends(get_async_db)) -> RSPermission:
    try:
        result = await Permission.find_one(db, id)
        return result
    except Exception as e:
        print(e)
        raise e


@router.get('/', response_model=RSPermissionList, status_code=200, tags=[tag])
async def get_Permissions(pag: Optional[int] = 1, 
                            ord: Literal["asc", "desc"] = "asc", 
                            status: Literal["deleted", "exists", "all"] = "exists", 
                            db: AsyncSession = Depends(get_async_db)
                            ) -> RSPermissionList:
    try:
        result = await Permission.find_some(db, pag, ord, status)
        result = map(lambda x: RSPermission(
                 uid=x.uid,
                 action=x.action,
                 description=x.description,
                 name=x.name,
                 type=x.type,
             ), result)
        return RSPermissionList(
            data=list(result),
            total=0,
            page=0,
            page_size=0,
            total_pages=0,
            has_next=False,
            has_prev=False,
            next_page=0,
            prev_page=0           
        )
    except Exception as e:
        print(e)
        raise e


@router.post('/', response_model=RSPermission, status_code=201, tags=[tag])
async def create_Permission(permission: RQPermission, db: AsyncSession = Depends(get_async_db)) -> RSPermission:
    try:
        result = await Permission(**permission.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete('/id/{id}', status_code=204, tags=[tag])
async def delete_Permission(id: str, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await Permission.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put('/id/{id}', response_model=RSPermission, status_code=200, tags=[tag])
async def update_Permission(id: str, permission: RQPermission, db: AsyncSession = Depends(get_async_db)) -> RSPermission:
    try:
        result = await Permission.update(db, id, permission.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e