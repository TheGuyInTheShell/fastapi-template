from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.permissions.models import Permission

from .models import Role
from .schemas import RQRole, RSRole
from app.modules.role_permissions.models import RolePermission


async def create_role(db: AsyncSession, rq_role: RQRole) -> RSRole:
    try:
        permissions = []

        if rq_role.permissions.__len__() == 0:
            raise HTTPException(
                status_code=400, detail="Role must have at least one permission"
            )

        for permission in tuple(rq_role.permissions):
            try:
                permission_obj = await Permission.find_one(db, permission)
                permissions.append(permission_obj.id)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=e.args[0])

        rq_role.permissions = permissions

        role = await Role(**rq_role.model_dump()).save(db)
        role_id = role.id

        # Sync Pivot Table (RolePermission)
        for perm_id in permissions:
            await RolePermission(
                role_id=role_id,
                permission_id=perm_id
            ).save(db)

        return role

    except Exception as e:
        raise e
