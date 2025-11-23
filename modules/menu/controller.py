from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import Menu
from .schemas import RQMenu, RSMenu, RSMenuList

# prefix /menu
router = APIRouter()
tag = 'menu'

@router.get("/id/{id}", response_model=RSMenu, status_code=200, tags=[tag])
async def get_Permission(id: str, db: AsyncSession = Depends(get_async_db)) -> RSMenu:
    try:
        result = await Menu.find_one(db, id)
        return result
    except Exception as e:
        print(e)
        raise e


@router.get("/", response_model=RSMenuList, status_code=200, tags=[tag])
async def get_Permissions(
    pag: Optional[int] = 1,
    ord: Literal["asc", "desc"] = "asc",
    status: Literal["deleted", "exists", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RSMenuList:
    try:
        result = await Menu.find_some(db, pag, ord, status)
        result = map(
            lambda x: RSMenu(
                uid=x.uid,
                active=x.active,
                file_route=x.file_route,
                name=x.name,
                type_menu=x.type_menu,
            ),
            result,
        )
        return RSMenuList(
            data=list(result),
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


@router.post("/", response_model=RSMenu, status_code=201, tags=[tag])
async def create_Permission(
    menu: RQMenu, db: AsyncSession = Depends(get_async_db)
) -> RSMenu:
    try:
        result = await Menu(**menu.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete("/id/{id}", status_code=204, tags=[tag])
async def delete_Permission(id: str, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await Menu.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put("/id/{id}", response_model=RSMenu, status_code=200, tags=[tag])
async def update_Permission(
    id: str, menu: RQMenu, db: AsyncSession = Depends(get_async_db)
) -> RSMenu:
    try:
        result = await Menu.update(db, id, menu.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e
