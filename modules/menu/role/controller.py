from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db
from .models import MenuRole
from .schemas import RQMenuRole, RSMenuRole, RSMenuRoleList

# prefix /menu
router = APIRouter()
tag = 'menu - roles'
    

@router.get('id/{id}', response_model=RSMenuRole, status_code=200, tags=[tag])
async def get_Permission(id: str, db: AsyncSession = Depends(get_async_db)) -> RSMenuRole:
    try:
        result = await MenuRole.find_one(db, id)
        return result
    except Exception as e:
        print(e)
        raise e


@router.get('/', response_model=RSMenuRoleList, status_code=200, tags=[tag])
async def get_Permissions(pag: Optional[int] = 1, 
                            ord: Literal["asc", "desc"] = "asc", 
                            status: Literal["deleted", "exists", "all"] = "exists", 
                            db: AsyncSession = Depends(get_async_db)
                            ) -> RSMenuRoleList:
    try:
        result = await MenuRole.find_some(db, pag, ord, status)
        result = map(lambda x: RSMenuRole(
                 uid=x.uid,
                 description=x.description,
                 disabled=x.disabled,
                 name=x.name,
                 level=x.level,
                 menus=x.menus,
             ), result)
        return RSMenuRoleList(
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


@router.post('/', response_model=RSMenuRole, status_code=201, tags=[tag])
async def create_Permission(menu_role: RQMenuRole, db: AsyncSession = Depends(get_async_db)) -> RSMenuRole:
    try:
        result = await MenuRole(**menu_role.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete('id/{id}', status_code=204, tags=[tag])
async def delete_Permission(id: str, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await MenuRole.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put('id/{id}', response_model=RSMenuRole, status_code=200, tags=[tag])
async def update_Permission(id: str, menu_role: RQMenuRole, db: AsyncSession = Depends(get_async_db)) -> RSMenuRole:
    try:
        result = await MenuRole.update(db, id, menu_role.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e