
from sqlalchemy.future import select

from modules.permissions.models import Permission
from modules.roles.models import Role
from modules.permissions.const import admin_type

from core.database import SessionAsync




async def has_permission(db: SessionAsync, role_id: str, route_name: str, method: str):
    try:
        permission = await db.execute(select(Permission).where(Permission.name == route_name, Permission.action == method, Permission.type == admin_type))
        
        permission = permission.scalar_one_or_none()
        
        if permission is None:
            return False

        role = await Role.find_one(db, role_id)
        
        if role is None:
            return False

        if permission.id in set(role.permissions):
            return True

        return False
    except Exception as e:
        print(e)
        return False 