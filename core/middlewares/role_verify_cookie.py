from .jwt_verify import JWT_VERIFY
from app.modules.auth.services import decode_token, create_token, TokenData
import time
import asyncio
from fastapi import Request, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from app.modules.roles.models import Role
from app.modules.permissions.models import Permission
from app.modules.users.models import User
from app.modules.users.schemas import RSUserTokenData
from app.modules.permissions.const import admin_type
from core.database import get_async_db, SessionAsync
from starlette.status import HTTP_401_UNAUTHORIZED


async def ROLE_VERIFY_COOKIE(request: Request, response: Response) -> RSUserTokenData:
    try:        
        # Get access token from cookies
        access_token = request.cookies.get("access_token")
        refresh_token_cookie = request.cookies.get("refresh_token")
        
        payload = None

        # Try access token
        if access_token:
            try:
                payload = await JWT_VERIFY(access_token)
            except Exception as e:
                payload = None

        # If no valid access token, try refresh token
        if not payload:
            refresh_token = request.cookies.get("refresh_token")
            if refresh_token:
                refresh_payload = decode_token(refresh_token)
                if refresh_payload and refresh_payload.type == "refresh":
                    new_payload: TokenData = refresh_payload
                    new_access_token = create_token(
                        data={
                            "sub": new_payload.sub,
                            "email": new_payload.email,
                            "role": new_payload.role,
                            "full_name": new_payload.full_name,
                            "id": new_payload.id,
                            "uid": new_payload.uid,
                        }
                    )

                    # Set new access token cookie
                    response.set_cookie(
                        key="access_token",
                        value=new_access_token,
                        httponly=True,
                        secure=True,
                        samesite="lax",
                    )

                    payload = new_payload
                else:
                    payload = None

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Invalid role",
                headers={"Location": "/admin/sign-in"},
            )

        db = SessionAsync()

        # Get user's role and permissions

        if not payload.role:
            await db.close()
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Invalid role",
                headers={"Location": "/admin/sign-in"},
            )
        
        role: Role = await Role.find_one(db, payload.role)
        if not role:
            await db.close()
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Invalid role",
                headers={"Location": "/admin/sign-in"},
            )

        permissions_users = set(role.permissions)

        # Get required permission for this route
        route_name = request.scope["route"].name
        method = request.method

        permission_require = (
            await db.execute(
                select(Permission).where(
                    Permission.name == route_name,
                    Permission.action == method,
                    Permission.type == admin_type,
                )
            )
        ).scalar_one_or_none()

        await db.close()

        # Check if permission exists and user has it
        if not permission_require:
            user_data = RSUserTokenData(
                id=payload.id or 0,
                uid=payload.uid or (payload.id if isinstance(payload.id, str) else ""),
                username=payload.sub,
                email=payload.email or "",
                full_name=payload.full_name or "",
                role=payload.role or "",
                otp_enabled=payload.otp_enabled,
            )
            request.state.user = user_data
            return user_data

        if permission_require.id in permissions_users:
            user_data = RSUserTokenData(
                id=payload.id or 0,
                uid=payload.uid or (payload.id if isinstance(payload.id, str) else ""),
                username=payload.sub,
                email=payload.email or "",
                full_name=payload.full_name or "",
                role=payload.role or "",
                otp_enabled=payload.otp_enabled,
            )
            request.state.user = user_data
            return user_data
        else:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Invalid role",
                headers={"Location": "/admin/sign-in"},
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Authentication error",
            headers={"Location": "/admin/sign-in"},
        )
