from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.permissions.models import Permission
from app.modules.permissions.meta.models import MetaPermissions
from .const import DEFAULT_MENU

async def ensure_default_menu(session: AsyncSession):
    # Check if any menu permission exists (to avoid duplicates or re-seeding)
    
    try:
        for item in DEFAULT_MENU:
            stmt = select(Permission).where(Permission.name == item["name"])
            result = await session.execute(stmt)
            perm = result.scalar_one_or_none()
            
            if not perm:
                perm = Permission(name=item["name"], action=item["action"], type=item["type"], description=item["desc"])
                session.add(perm)
                await session.flush() # get ID
            
            # Check/Add Meta for both new and existing permissions
            for k, v in item["meta"].items(): # type: ignore
                # Check if this meta key already exists for this permission
                meta_stmt = select(MetaPermissions).where(
                    MetaPermissions.ref_permission == perm.id,
                    MetaPermissions.key == k
                )
                meta_result = await session.execute(meta_stmt)
                existing_meta = meta_result.scalar_one_or_none()
                
                if not existing_meta:
                    meta = MetaPermissions(ref_permission=perm.id, key=k, value=v)
                    session.add(meta)
        
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
