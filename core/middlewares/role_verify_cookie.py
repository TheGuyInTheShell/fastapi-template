from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.future import select

from core.database.async_connection import SessionAsync
from modules.auth.controller import oauth2_schema
from modules.auth.schemas import RSUser
from modules.permissions.models import Permission
from modules.roles.models import Role

from .jwt_verify import JWT_VERIFY
import asyncio


async def ROLE_VERIFY_COOKIE(request: Request) -> RSUser:
    try:
        db = SessionAsync()
        payload = await JWT_VERIFY(request.cookies.get("access_token"))
        role: Role = await Role.find_one(db, payload["role"])
        permissions_users = role.permissions
        (name,) = (request.scope["route"].name,)
        method = request.method
        permission_require = (
            await db.execute(
                select(Permission).where(
                    Permission.name == name,
                    Permission.action == method,
                    Permission.type == "PANEL",
                )
            )
        ).scalar_one_or_none()
        asyncio.ensure_future(db.close())
        if permission_require.uid in permissions_users:
            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise e
