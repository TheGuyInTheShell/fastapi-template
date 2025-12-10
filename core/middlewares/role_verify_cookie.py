
from .jwt_verify import JWT_VERIFY
import asyncio
from fastapi import Request, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from modules.roles.models import Role
from modules.permissions.models import Permission
from modules.users.models import User
from modules.users.schemas import RSUserTokenData
from core.database import get_async_db, SessionAsync
from starlette.status import HTTP_401_UNAUTHORIZED


async def ROLE_VERIFY_COOKIE(request: Request) -> RSUserTokenData:
    try:
        # Get access token from cookies
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Invalid role", headers={"Location": "/admin/sign-in"})
        
        # Verify JWT and get payload
        db = SessionAsync()
        payload = await JWT_VERIFY(access_token)
        
        # Get user's role and permissions
        role: Role = await Role.find_one(db, payload["role"])
        if not role:
            await db.close()
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Invalid role", headers={"Location": "/admin/sign-in"})
        
        permissions_users = set(role.permissions)
        
        # Get required permission for this route
        route_name = request.scope["route"].name
        method = request.method
        
        permission_require = (
            await db.execute(
                select(Permission).where(
                    Permission.name == route_name,
                    Permission.action == method,
                    Permission.type == "PANEL",
                )
            )
        ).scalar_one_or_none()
        
        await db.close()
        
        # Check if permission exists and user has it
        if not permission_require:
            # No permission requirement found for this route - allow access
            return RSUserTokenData(
                uid=payload["id"],
                username=payload["sub"],
                email=payload["email"],
                full_name=payload["full_name"],
                role=payload["role"],
            )
        
        if permission_require.uid in permissions_users:
            return RSUserTokenData(
                uid=payload["id"],
                username=payload["sub"],
                email=payload["email"],
                full_name=payload["full_name"],
                role=payload["role"],
            )
        else:
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Invalid role", headers={"Location": "/admin/sign-in"})
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Invalid role", headers={"Location": "/admin/sign-in"})
    except Exception as e:
        # Convert any other exception to 401 Unauthorized
        print(f"Error in ROLE_VERIFY_COOKIE: {e}")
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Invalid role", headers={"Location": "/admin/sign-in"})
