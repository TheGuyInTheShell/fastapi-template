from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from models.user import User
from schemas.user import INUser, RQUser, RSUser
from typing import Union
from .types import TokenData
import time
import jwt
from dotenv import load_dotenv
import os
load_dotenv()

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY_JWT = os.environ.get("JWT_KEY").encode()
USED_ALGORITHM = os.environ.get("JWT_ALG")


async def get_user(db: AsyncSession, username: str) -> INUser | None:
    try:
        query = await db.execute(select(User).where(User.username == username))
        user = query.scalar_one_or_none()
        if user:
            return INUser(
                id=user.id,
                username=user.username,
                password=user.password,
                disable=user.disable,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
            )
        else:
            return None
    except ValueError as e:
        print(e)
        return None


def verify_password(plane_password: str, current_password: str) -> bool:
    return hash_context.verify(plane_password, current_password)


async def authenticade_user(db: AsyncSession, username: str, password: str) -> RSUser:
    try:
        user = await get_user(db, username)
        if not user:
            return
        same_passowords = verify_password(password, user.password)
        if not same_passowords:
            return
        return RSUser(
            id=user.id,
            username=user.username,
            disable=user.disable,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        )
    except ValueError as e:
        print(e)
        raise e
    

async def create_user(db: AsyncSession, user_data: RQUser)-> RSUser | None:
    try:
        user = User(
            username=user_data.username,
            password=hash_context.hash(user_data.password),
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role.value,
            disable=False,
            )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return RSUser(
            id=user.id,
            username=user.username,
            disable=user.disable,
            email=user.email,
            full_name=user.full_name,
            role=user.role
        )
    except ValueError as e:
        print(e)
        return None
    

async def create_token(data: dict, expires_time: Union[float, None] = None) -> str:
    print(time.time())
    if expires_time is None:
        expires = time.time() + 600
    else:
        expires = time.time() + expires_time
    copy_user = data.copy()
    copy_user.update({"exp": expires})
    token_jwt = jwt.encode(copy_user, key=SECRET_KEY_JWT, algorithm=USED_ALGORITHM)
    return token_jwt


def decode_token(token: str) -> TokenData | None:
    try:
        decode_cotent: TokenData = jwt.decode(token, key=SECRET_KEY_JWT, algorithms=USED_ALGORITHM)
        return decode_cotent if decode_cotent['exp'] >= time.time() else None
    except:
        return None
