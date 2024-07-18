import os
from importlib import import_module
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db

from .models import ApiToken
from .schemas import RQApiToken, RSApiToken, RSApiTokensList
from .services import save_token

# prefix /tokens
router = APIRouter()

tag = "tokens"


@router.get("/id/{id}", response_model=RSApiToken, tags=[tag])
async def get_token(id: str, db: AsyncSession = Depends(get_async_db)) -> RSApiToken:
    try:
        result = await ApiToken.find_one(db, id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=RSApiTokensList, tags=[tag])
async def get_tokens(
    pag: Optional[int] = 1,
    ord: Literal["desc", "asc"] = "asc",
    status: Literal["exists", "deleted", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RSApiTokensList:
    try:
        result = await ApiToken.find_some(db, pag, ord, status)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/id/{id}", response_model=RSApiToken, tags=[tag])
async def delete_tokens(
    id: str, db: AsyncSession = Depends(get_async_db)
) -> RSApiToken:
    try:
        result = await ApiToken.delete(db, id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=RSApiToken, tags=[tag])
async def create_token(
    rq_vehicle: RQApiToken,
    client_id: str,
    client_type: Literal["persons", "privates", "publics"],
    db: AsyncSession = Depends(get_async_db),
) -> RSApiToken:
    try:
        result = await save_token(db, rq_vehicle, client_id, client_type)
        return result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/id/{id}", response_model=RSApiToken, status_code=200, tags=[tag])
async def update_token(
    id: str, subscription: RQApiToken, db: AsyncSession = Depends(get_async_db)
) -> RSApiToken:
    try:
        result = await ApiToken.update(db, id, subscription.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e


# ----------------------------------------------------- #
module_names = [f for f in os.listdir("modules/vehicles")]

for module_name in module_names:
    try:
        if module_name.find(".py") != -1 or module_name.find("pycache") != -1:
            continue
        module = import_module(f"modules.tokens.{module_name}.controller")
        router.include_router(module.router, prefix=f"/{module_name}")
    except Exception as e:
        print(f"Error importing module {module_name}: {e}")
        continue
