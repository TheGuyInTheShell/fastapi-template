from sqlalchemy.ext.asyncio import AsyncSession

from .models import MetaUsers
from app.modules.users.models import User

async def create_meta_users(
    db: AsyncSession,
    key: str,
    value: str,
    ref_user: int,
) -> MetaUsers:
    """
    Create a new meta in the database.
    
    Args:
        db: Database session
        key: Key of the meta
        value: Value of the meta
        ref_user: Reference to the user
        
    Returns:
        MetaUsers: The created meta
    """
    meta_obj = MetaUsers(
        key=key,
        value=value,
        ref_user=await User.find_one(db, ref_user),
    )
    await meta_obj.save(db)
    return meta_obj


async def get_meta_users(
    db: AsyncSession,
    id: int | str,
) -> MetaUsers:
    """
    Get a meta by ID from the database.
    
    Args:
        db: Database session
        id: ID of the meta
        
    Returns:
        MetaUsers: The meta with the given ID
    """
    return await MetaUsers.find_one(db, id)


async def get_meta_users_all(
    db: AsyncSession,
    page: int = 1,
    order: str = "asc",
    status: str = "exists",
) -> list[MetaUsers]:
    """
    Get all metas from the database.
    
    Args:
        db: Database session
        page: Page number
        order: Order of the metas
        status: Status of the metas
        
    Returns:
        list[MetaUsers]: List of metas
    """
    return await MetaUsers.find_some(db, page, order, status)


async def delete_meta_users(
    db: AsyncSession,
    id: int | str,
) -> None:
    """
    Delete a meta from the database.
    
    Args:
        db: Database session
        id: ID of the meta
    """
    await MetaUsers.delete(db, id)


async def update_meta_users(
    db: AsyncSession,
    id: int | str,
    key: str,
    value: str,
    ref_user: int,
) -> MetaUsers:
    """
    Update a meta in the database.
    
    Args:
        db: Database session
        id: ID of the meta
        key: Key of the meta
        value: Value of the meta
        ref_user: Reference to the user
        
    Returns:
        MetaUsers: The updated meta
    """
    meta_obj = await MetaUsers.find_one(db, id)
    meta_obj.key = key
    meta_obj.value = value
    meta_obj.ref_user = ref_user
    await meta_obj.save(db)
    return meta_obj
