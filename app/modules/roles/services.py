from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.permissions.models import Permission

from .models import Role
from .schemas import RQRole, RSRole


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

        return role

    except Exception as e:
        raise e
