from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from modules.users.models import User
from core.cache import Cache

from .schemas import RQUser, RQUserLogin, RSUser, RSUserTokenData
from .services import (
    authenticade_user,
    create_refresh_token,
    create_token,
    create_user,
    decode_token,
    get_user,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)

# prefix /auth
router = APIRouter()

cache = Cache()

oauth2_schema = OAuth2PasswordBearer("auth/sign-in")
tag = 'auth'

@router.get("/", tags=[tag])
@cache.cache_endpoint(ttl=120, namespace="auth")
def token(token: str = Depends(oauth2_schema)):
    return token


@router.post("/sign-in", tags=[tag])
async def sign_in(user_data: RQUserLogin, db: AsyncSession = Depends(get_async_db)):
    try:
        user = await authenticade_user(
            db, username=user_data.username, password=user_data.password
        )
        if user is None:
            raise HTTPException(
                status_code=401, detail="Incorrect username or password"
            )
        
        # Create access token
        access_token = create_token(
            data={
                "sub": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "id": user.uid,
            }
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={
                "sub": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "id": user.uid,
            }
        )
        
        # Create response with JWTs in body (optional for refresh_token, but useful)
        response = JSONResponse(
            content={
                "access_token": access_token, 
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        )
        
        # Set Access Token in HTTP-only cookie (existing behavior)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            # max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, # Use if imported or hardcode
            samesite="lax",
            # secure=True,
        )

        # Set Refresh Token in HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            path="/auth/refresh",
            samesite="lax",
            # secure=True,
        )
        
        return response
    except ValueError as e:
        print(e)
        raise e


@router.post("/refresh", tags=[tag])
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None)
):
    if not refresh_token:
        # Also check Authorization header or body if needed, but cookie is primary
        raise HTTPException(
            status_code=401, detail="Refresh token missing"
        )
        
    token_data = decode_token(refresh_token)
    
    # decode_token returns a dict or TokenData. Based on services.py it returns jwt.decode result which is dict but typed as TokenData. 
    # Let's assume dict access for safety or convert to model.
    if not token_data:
        raise HTTPException(
            status_code=401, detail="Invalid refresh token"
        )
        
    # Check token type
    # If token_data is a dict:
    type_ = token_data.get("type") if isinstance(token_data, dict) else getattr(token_data, "type", None)
    
    if type_ != "refresh":
         raise HTTPException(
            status_code=401, detail="Invalid token type"
        )

    # Allow token rotation? For now just issue new access token.
    # We can also issue a new refresh token if we want to rotate them.
    
    # Extract user data
    username = token_data.get("sub") if isinstance(token_data, dict) else token_data.sub
    email = token_data.get("email") if isinstance(token_data, dict) else token_data.email
    role = token_data.get("role") if isinstance(token_data, dict) else token_data.role
    full_name = token_data.get("full_name") if isinstance(token_data, dict) else token_data.full_name
    uid = token_data.get("id") if isinstance(token_data, dict) else token_data.id

    new_access_token = create_token(
        data={
            "sub": username,
            "email": email,
            "role": role,
            "full_name": full_name,
            "id": uid,
        }
    )
    
    response = JSONResponse(
        content={"access_token": new_access_token, "token_type": "bearer"}
    )
    
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
    )
    
    return response


@router.post("/sign-up", response_model=RSUser, tags=[tag])
async def sign_up(
    form_sign_up: RQUser, db: AsyncSession = Depends(get_async_db)
) -> RSUser | None:
    try:
        query = await User.find_by_colunm(db, "username", form_sign_up.username)
        exists_user = query.scalar_one_or_none()
        if exists_user:
            raise HTTPException(
                status_code=401,
                detail="Nombre de usuario tomado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        result = await create_user(db, form_sign_up)
        if not result:
            raise HTTPException(status_code=500, detail="Error al crear el usuario")
        return result
    except ValueError as e:
        print(e)
        raise e
