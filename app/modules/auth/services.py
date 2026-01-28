from core.config.globals import settings
import time
from typing import Union
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_async_db

from app.modules.users.models import User
from core.services.init_subscriber import initialize_subscriber_role

from .schemas import INUser, RQUser, RSUser
from .types import TokenData

import bcrypt
from bcrypt import _bcrypt # type: ignore
from fastapi.security import OAuth2PasswordBearer

oauth2_schema = OAuth2PasswordBearer("auth/sign-in")

if not hasattr(bcrypt, "__about__"):
   setattr(bcrypt, "__about__", type("About", (object,), {"__version__": _bcrypt.__version_ex__}))

import jwt

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY_JWT = settings.JWT_KEY.encode()
USED_ALGORITHM = settings.JWT_ALG


async def get_user(db: AsyncSession, username: str) -> User | None:
    try:
        query = await User.find_by_colunm(db, "username", username)
        user = query.scalar_one_or_none()
        return user
    except ValueError as e:
        print(e)
        return None


def verify_password(plane_password: str, current_password: str) -> bool:
    return hash_context.verify(plane_password, current_password)


async def authenticade_user(db: AsyncSession, username: str, password: str) -> RSUser:
    try:
        user = await get_user(db, username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        same_passowords = verify_password(password, user.password)
        if same_passowords is False:
            raise HTTPException(status_code=401, detail="Incorrect password")
        result = RSUser(
            uid=user.uid,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role_ref,
            otp_enabled=user.otp_enabled,
        )
        return result
    except ValueError as e:
        print(e)
        raise e


ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


async def create_user(db: AsyncSession, user_data: RQUser) -> dict | None:
    try:
        subscriber_role = await initialize_subscriber_role(db)
        user = await User(
            username=user_data.username,
            password=hash_context.hash(user_data.password),
            email=user_data.email,
            full_name=user_data.full_name,
            role_ref=subscriber_role.uid,
        ).save(db)

        return {
            "uid": user.uid,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role_ref,
        }
    except ValueError as e:
        print(e)
        raise e


def create_token(data: dict, expires_time: Union[float, None] = None) -> str:
    current_time = int(time.time())
    if expires_time is None:
        expires = current_time + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    else:
        expires = current_time + int(expires_time)
    copy_user = data.copy()
    if "type" not in copy_user:
        copy_user["type"] = "access"
    copy_user.update({"exp": expires, "iat": current_time})
    token_jwt = jwt.encode(copy_user, key=SECRET_KEY_JWT, algorithm=USED_ALGORITHM)
    return token_jwt


def create_refresh_token(data: dict, expires_time: Union[float, None] = None) -> str:
    current_time = int(time.time())
    if expires_time is None:
        expires = current_time + (REFRESH_TOKEN_EXPIRE_MINUTES * 60)
    else:
        expires = current_time + int(expires_time)
    copy_user = data.copy()
    copy_user.update({"exp": expires, "type": "refresh", "iat": current_time})
    token_jwt = jwt.encode(copy_user, key=SECRET_KEY_JWT, algorithm=USED_ALGORITHM)
    return token_jwt


def decode_token(token: str) -> TokenData | None:
    try:
        decode_cotent: dict = jwt.decode(
            token, key=SECRET_KEY_JWT, algorithms=[USED_ALGORITHM]
        )
        exp_time = decode_cotent.get("exp", 0)
        current_time = time.time()
        is_valid_time = exp_time > current_time
        if not is_valid_time:
            return None

        return TokenData(**decode_cotent)
    except Exception as e:
        return None

# We need a dependency to get current user from token for these protected endpoints
async def get_current_user(token: str = Depends(oauth2_schema), db: AsyncSession = Depends(get_async_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    query = await User.find_by_colunm(db, "username", payload.sub)
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user