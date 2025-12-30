from sqlalchemy.future import select

from app.modules.permissions.models import Permission
from app.modules.roles.models import Role
from app.modules.permissions.const import admin_type

from core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


async def has_permission(db: AsyncSession, role_id: str, route_name: str, method: str):
    try:
        
        query = await db.execute(
            select(Permission).where(
                Permission.name == route_name,
                Permission.action == method,
                Permission.type == admin_type,
            )
        )

        permission = query.scalar_one_or_none()
        
        if permission is None:
            return False
        

        role = await Role.find_one(db, role_id)

        if role is None:
            return False
        

        if permission.uid in set(role.permissions):
            return True
        
        return False
    except Exception as e:
        return False
