from fastapi import Depends, HTTPException, Request, status, Response
from sqlalchemy.future import select
from core.database import SessionAsync
from app.modules.auth.controller import oauth2_schema
from app.modules.auth.schemas import RSUser
from app.modules.auth.services import decode_token, create_token
from app.modules.permissions.models import Permission
from app.modules.role_permissions.models import RolePermission
from app.modules.permissions.const import api_type
from typing import Callable
from .jwt_verify import JWT_VERIFY
from core.config.globals import settings

mode = settings.MODE


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
                    if refresh_payload and refresh_payload.type == "refresh":
                        payload = refresh_payload
                        # Issue new access token
                        new_access_token = create_token(
                            data={
                                "sub": payload.sub,
                                "email": payload.email,
                                "role": payload.role,
                                "full_name": payload.full_name,
                                "id": payload.id,
                                "uid": payload.uid,
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

            if not payload.role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User unauthorized",
                    headers={"WWW-Authenticate": "Bearer"},
                )

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

            if not permission_require:
                await db.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User unauthorized",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check if user has permission via pivot table
            has_permission = (
                await db.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == payload.role,
                        RolePermission.permission_id == permission_require.id
                    )
                )
            ).scalar_one_or_none()

            await db.close()

            if has_permission:
                return RSUser(
                    id=payload.id or 0,
                    uid=payload.uid or (payload.id if isinstance(payload.id, str) else ""),
                    username=payload.sub,
                    email=payload.email or "",
                    full_name=payload.full_name or "",
                    role=payload.role or "",
                    otp_enabled=payload.otp_enabled,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User unauthorized",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        except Exception as e:
            raise e

    return ROLE_VERIFY_CURRY
