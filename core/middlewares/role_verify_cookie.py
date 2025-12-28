from .jwt_verify import JWT_VERIFY
from modules.auth.services import decode_token, create_token, TokenData
import time
import asyncio
from fastapi import Request, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from modules.roles.models import Role
from modules.permissions.models import Permission
from modules.users.models import User
from modules.users.schemas import RSUserTokenData
from modules.permissions.const import admin_type
from core.database import get_async_db, SessionAsync
from starlette.status import HTTP_401_UNAUTHORIZED


async def ROLE_VERIFY_COOKIE(request: Request, response: Response) -> RSUserTokenData:
    try:
        # Get access token from cookies
        access_token = request.cookies.get("access_token")
        payload = None

        # Try access token
        if access_token:
            try:
                payload = await JWT_VERIFY(access_token)
            except Exception:
                payload = None

        # If no valid access token, try refresh token
        if not payload:
            refresh_token = request.cookies.get("refresh_token")
            if refresh_token:
                # Check refresh token
                refresh_payload = decode_token(refresh_token)
                if refresh_payload and refresh_payload.type == "refresh":
                    # Refresh is valid
                    new_payload: TokenData = refresh_payload

                    # Create new access token
                    new_access_token = create_token(
                        data={
                            "sub": new_payload.sub,
                            "email": new_payload.email,
                            "role": new_payload.role,
                            "full_name": new_payload.full_name,
                            "id": new_payload.id,
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

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Invalid role",
                headers={"Location": "/admin/sign-in"},
            )

        db = SessionAsync()

        # Get user's role and permissions
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
        # Check if permission exists and user has it
        if not permission_require:
             # No permission requirement found for this route - allow access
            user_data = RSUserTokenData(
                uid=payload.id or "",
                username=payload.sub,
                email=payload.email or "",
                full_name=payload.full_name or "",
                role=payload.role or "",
            )
            request.state.user = user_data
            return user_data

        if permission_require.uid in permissions_users:
            user_data = RSUserTokenData(
                uid=payload.id or "",
                username=payload.sub,
                email=payload.email or "",
                full_name=payload.full_name or "",
                role=payload.role or "",
            )
            request.state.user = user_data
            return user_data
        else:
            raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                detail="Invalid role",
                headers={"Location": "/admin/sign-in"},
            )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Invalid role",
            headers={"Location": "/admin/sign-in"},
        )
    except Exception as e:
        # Convert any other exception to 401 Unauthorized
        print(f"Error in ROLE_VERIFY_COOKIE: {e}")
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Invalid role",
            headers={"Location": "/admin/sign-in"},
        )
