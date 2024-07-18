from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from modules.permissions.models import Permission

from .models import Role
from .schemas import RQRole, RSRole


async def create_role(db: AsyncSession, rq_role: RQRole) -> RSRole:
    try: 
        permissions: list[str]  = []
        
        if rq_role.permissions.__len__() == 0:
            raise HTTPException(status_code=400, detail="Role must have at least one permission")
        
        rq_role.permissions = tuple(rq_role.permissions)
        
        for permission in rq_role.permissions:
            try: 
                permissions.append((await Permission.find_one(db, permission)).uid)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=e.args[0]) 
        
        rq_role.permissions = permissions
        
        role = await Role(**rq_role.model_dump()).save(db)
        
        return role
        
    except Exception as e:
        raise e 
     