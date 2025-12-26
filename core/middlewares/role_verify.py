from fastapi import Depends, HTTPException, Request, status, Response

from fastapi.security import HTTPBearer

from sqlalchemy.future import select


from core.database import get_async_db

from modules.auth.controller import oauth2_schema

from modules.auth.schemas import RSUser
from modules.auth.services import decode_token, create_token

from modules.permissions.models import Permission
from modules.roles.models import Role
from modules.permissions.const import api_type

from core.database import SessionAsync

from typing import Callable

import asyncio


from .jwt_verify import JWT_VERIFY


import os
import dotenv

dotenv.load_dotenv()

mode = os.getenv("MODE")


def ROLE_VERIFY(omit_routes: list = []) -> Callable:
    def ROLE_VERIFY_PASS(request: Request):
        return True

    if mode == "DEVELOPMENT":
        return ROLE_VERIFY_PASS

    async def ROLE_VERIFY_CURRY(
        request: Request, response: Response, access_token: str = Depends(oauth2_schema)
    ) -> RSUser:
        try:
            db = SessionAsync()
            try:
                payload = await JWT_VERIFY(access_token)
            except Exception:
                payload = None

            # If access_token invalid, try refresh token from header
            if not payload:
                refresh_token = request.headers.get("refresh-token")
                # Also check x-refresh-token just in case
                if not refresh_token:
                    refresh_token = request.headers.get("x-refresh-token")

                if refresh_token:
                    refresh_payload = decode_token(refresh_token)
                    if refresh_payload and refresh_payload.get("type") == "refresh":
                        payload = refresh_payload
                        # Issue new access token
                        new_access_token = create_token(
                            data={
                                "sub": payload["sub"],
                                "email": payload["email"],
                                "role": payload["role"],
                                "full_name": payload.get("full_name"),
                                "id": payload.get("id"),
                            }
                        )
                        # Set metadata in response header
                        response.headers["new-access-token"] = new_access_token

            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User unauthorized",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            role: Role = await Role.find_one(db, payload["role"])

            permissions_users = set(role.permissions)

            (name,) = (request.scope["route"].name,)

            method = request.method

            permission_require = (
                await db.execute(
                    select(Permission).where(
                        Permission.name == name,
                        Permission.action == method,
                        Permission.type == api_type,
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

    return ROLE_VERIFY_CURRY
