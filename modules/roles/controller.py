from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import Role
from .schemas import RQRole, RSRole, RSRoleList
from .services import create_role

# prefix /roles
router = APIRouter()
tag = 'roles'

@router.get('/id/{id}', response_model=RSRole, status_code=200, tags=[tag])
async def get_Role(id: str, db: AsyncSession = Depends(get_async_db)) -> RSRole:
    try:
        result = await Role.find_one(db, id)
        return result
    except Exception as e:
        print(e)
        raise e


@router.get('/', response_model=RSRoleList, status_code=200, tags=[tag])
async def get_Roles(pag: Optional[int] = 1, 
                            ord: Literal["asc", "desc"] = "asc", 
                            status: Literal["deleted", "exists", "all"] = "exists", 
                            db: AsyncSession = Depends(get_async_db)
                            ) -> RSRoleList:
    try:
        result = await Role.find_some(db, pag, ord, status)
        result = map(lambda x: RSRole(
            uid=x.uid,
            description=x.description,
            name=x.name,
            level=x.level,
            permissions=x.permissions,
             ), result)
        return RSRoleList(
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


@router.post('/', response_model=RSRole, status_code=201, tags=[tag])
async def create_Role(role: RQRole, db: AsyncSession = Depends(get_async_db)) -> RSRole:
    try:
        result = await create_role(db, role)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete('/id/{id}', status_code=204, tags=[tag])
async def delete_Role(id: str, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await Role.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put('/id/{id}', response_model=RSRole, status_code=200, tags=[tag])
async def update_Role(id: str, role: RQRole, db: AsyncSession = Depends(get_async_db)) -> RSRole:
    try:
        result = await Role.update(db, id, role.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e