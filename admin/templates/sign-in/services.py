from sqlalchemy.future import select

from app.modules.permissions.models import Permission
from app.modules.roles.models import Role
from app.modules.permissions.const import admin_type

from core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


async def has_permission(db: AsyncSession, role_id: str, route_name: str, method: str):
    try:
        print(f"[has_permission] Checking: role_id={role_id}, route={route_name}, method={method}")
        
        query = await db.execute(
            select(Permission).where(
                Permission.name == route_name,
                Permission.action == method,
                Permission.type == admin_type,
            )
        )

        permission = query.scalar_one_or_none()
        
        if permission is None:
            print(f"[has_permission] ❌ Permission not found for route: {route_name} {method}")
            return False
        
        print(f"[has_permission] ✓ Permission found: {permission.uid}")

        role = await Role.find_one(db, role_id)

        if role is None:
            print(f"[has_permission] ❌ Role not found: {role_id}")
            return False
        
        print(f"[has_permission] ✓ Role found: {role.name} with {len(role.permissions)} permissions")

        if permission.uid in set(role.permissions):
            print(f"[has_permission] ✅ Permission granted!")
            return True
        
        print(f"[has_permission] ❌ Permission denied - user doesn't have this permission")
        return False
    except Exception as e:
        print(f"[has_permission] ⚠️ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
