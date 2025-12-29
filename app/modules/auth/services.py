import os
import time
from typing import Union

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from core.services.init_subscriber import initialize_subscriber_role

from .schemas import INUser, RQUser, RSUser
from .types import TokenData

load_dotenv()

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY_JWT = os.environ.get("JWT_KEY", default="").encode() # type: ignore
USED_ALGORITHM = os.environ.get("JWT_ALG", default="HS256")


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
    if expires_time is None:
        expires = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    else:
        expires = time.time() + expires_time
    copy_user = data.copy()
    if "type" not in copy_user:
        copy_user["type"] = "access"
    copy_user.update({"exp": expires})
    token_jwt = jwt.encode(copy_user, key=SECRET_KEY_JWT, algorithm=USED_ALGORITHM)
    return token_jwt


def create_refresh_token(data: dict, expires_time: Union[float, None] = None) -> str:
    if expires_time is None:
        expires = time.time() + (REFRESH_TOKEN_EXPIRE_MINUTES * 60)
    else:
        expires = time.time() + expires_time
    copy_user = data.copy()
    copy_user.update({"exp": expires, "type": "refresh"})
    token_jwt = jwt.encode(copy_user, key=SECRET_KEY_JWT, algorithm=USED_ALGORITHM)
    return token_jwt


def decode_token(token: str) -> TokenData | None:
    try:
        decode_cotent: dict = jwt.decode(
            token, key=SECRET_KEY_JWT, algorithms=[USED_ALGORITHM]
        )
        return TokenData(**decode_cotent) if decode_cotent.get("exp", 0) >= time.time() else None
    except:
        return None
