from sqlalchemy.ext.asyncio import AsyncSession

from .models import Meta


async def create_meta(
    db: AsyncSession,
    name: str,
    description: str
) -> Meta:
    """
    Create a new meta in the database.
    
    Args:
        db: Database session
        name: Name of the meta
        description: Description of the meta
        
    Returns:
        Meta: The created meta
    """
    meta_obj = Meta(
        name=name,
        description=description,
    )
    await meta_obj.save(db)
    return meta_obj
