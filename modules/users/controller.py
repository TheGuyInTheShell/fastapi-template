from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from modules.auth.services import decode_token

from .models import User
from .schemas import RSUserTokenData

# prefix /users
router = APIRouter()

oauth2_schema = OAuth2PasswordBearer('/token')

tag = 'users'

@router.get('/me', response_model=RSUserTokenData, tags=[tag])
async def current_user(token: Annotated[str, Depends(oauth2_schema)]):
    try:
        if not token:
            raise HTTPException(status_code=401, detail="No autorizado", headers={
                    "WWW-Authenticate": "Bearer"
                })
        user_data = decode_token(token)
        return RSUserTokenData(
            id=user_data.id, 
            username=user_data.sub,
            role=user_data.role,
            full_name=user_data.full_name,
            email=user_data.email,
        )
    except ValueError as e:
        print(e)
        return "Error"
    
    
@router.get('', tags=[tag])
async def get_users(db: AsyncSession = Depends(get_async_db)):
    try:
        result = await User.find_some(db, status='exists')
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))