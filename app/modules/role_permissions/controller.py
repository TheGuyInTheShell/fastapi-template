from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from .schemas import RQAssignPermission, RQRemovePermission, RSRolePermissions
from .services import (
    assign_permission_to_role,
    remove_permission_from_role as remove_permission_from_role_service,
    get_role_permissions,
)
from core.cache import Cache

router = APIRouter()

cache = Cache()

tag = "role_permissions"


@router.get(
    "/role/{role_id}", response_model=RSRolePermissions, status_code=200, tags=[tag]
)
async def get_role_permissions_endpoint(
    role_id: int, db: AsyncSession = Depends(get_async_db)
) -> RSRolePermissions:
    """Get all permissions assigned to a role"""
    try:
        result = await get_role_permissions(db, role_id)
        return RSRolePermissions(
            role_id=result.role_id,
            role_name=result.role_name,
            permissions=result.permissions,
        )
    except Exception as e:
        print(e)
        raise e


@router.post("/assign", response_model=RSRolePermissions, status_code=200, tags=[tag])
async def assign_permission(
    request: RQAssignPermission, db: AsyncSession = Depends(get_async_db)
) -> RSRolePermissions:
    """Assign a permission to a role"""
    try:
        await assign_permission_to_role(db, request.role_id, request.permission_id)
        result = await get_role_permissions(db, request.role_id)
        return RSRolePermissions(
            role_id=result.role_id,
            role_name=result.role_name,
            permissions=result.permissions,
        )
    except Exception as e:
        print(e)
        raise e


@router.post("/remove", response_model=RSRolePermissions, status_code=200, tags=[tag])
async def remove_permission_from_role(
    request: RQRemovePermission, db: AsyncSession = Depends(get_async_db)
) -> RSRolePermissions:
    """Remove a permission from a role"""
    try:
        await remove_permission_from_role_service(db, request.role_id, request.permission_id)
        result = await get_role_permissions(db, request.role_id)
        return RSRolePermissions(
            role_id=result.role_id,
            role_name=result.role_name,
            permissions=result.permissions,
        )
    except Exception as e:
        print(e)
        raise e
