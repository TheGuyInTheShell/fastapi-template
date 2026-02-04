from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from app.modules.auth.services import decode_token

from .models import User
from .schemas import RSUserTokenData

# prefix /users
router = APIRouter()

oauth2_schema = OAuth2PasswordBearer("/token")

tag = "users"


@router.get("/me", response_model=RSUserTokenData, tags=[tag])
async def current_user(token: Annotated[str, Depends(oauth2_schema)]):
    try:
        if not token:
            raise HTTPException(
                status_code=401,
                detail="No autorizado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_data = decode_token(token)

        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return RSUserTokenData(
            id=user_data.id or 0,
            username=user_data.sub or "",
            role=user_data.role or 0,
            full_name=user_data.full_name or "",
            email=user_data.email or "",
        )
    except ValueError as e:
        print(e)
        return "Error"


@router.get("", tags=[tag])
async def get_users(db: AsyncSession = Depends(get_async_db)):
    try:
        result = await User.find_some(db, status="exists")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
