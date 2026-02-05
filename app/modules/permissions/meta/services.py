from sqlalchemy.ext.asyncio import AsyncSession

from .models import MetaPermissions
from app.modules.permissions.models import Permission


async def create_meta_permissions(
    db: AsyncSession,
    key: str,
    value: str,
    ref_permission: int,
) -> MetaPermissions:
    """
    Create a new meta_permissions in the database.
    
    Args:
        db: Database session
        key: Key of the meta_permissions
        value: Value of the meta_permissions
        ref_permission: Reference to the permission
        
    Returns:
        MetaPermissions: The created meta
    """
    meta_obj = MetaPermissions(
        key=key,
        value=value,
        ref_permission=await Permission.find_one(db, ref_permission),
    )
    await meta_obj.save(db)
    return meta_obj


async def get_meta_permissions(
    db: AsyncSession,
    id: int | str,
) -> MetaPermissions:
    """
    Get a meta_permissions by ID from the database.
    
    Args:
        db: Database session
        id: ID of the meta_permissions
        
    Returns:
        MetaPermissions: The meta_permissions with the given ID
    """
    return await MetaPermissions.find_one(db, id)


async def get_meta_permissions_all(
    db: AsyncSession,
    page: int = 1,
    order: str = "asc",
    status: str = "exists",
) -> list[MetaPermissions]:
    """
    Get all meta_permissions from the database.
    
    Args:
        db: Database session
        page: Page number
        order: Order of the meta_permissions
        status: Status of the meta_permissions
        
    Returns:
        list[MetaPermissions]: List of meta_permissions
    """
    return await MetaPermissions.find_some(db, page, order, status)


async def delete_meta_permissions(
    db: AsyncSession,
    id: int | str,
) -> None:
    """
    Delete a meta_permissions from the database.
    
    Args:
        db: Database session
        id: ID of the meta_permissions
    """
    await MetaPermissions.delete(db, id)


async def update_meta_permissions(
    db: AsyncSession,
    id: int | str,
    key: str,
    value: str,
    ref_permission: int,
) -> MetaPermissions:
    """
    Update a meta_permissions in the database.
    
    Args:
        db: Database session
        id: ID of the meta_permissions
        key: Key of the meta_permissions
        value: Value of the meta_permissions
        ref_permission: Reference to the permission
        
    Returns:
        MetaPermissions: The updated meta_permissions
    """
    meta_obj = await MetaPermissions.find_one(db, id)
    meta_obj.key = key
    meta_obj.value = value
    meta_obj.ref_permission = await Permission.find_one(db, ref_permission)
    await meta_obj.save(db)
    return meta_obj
