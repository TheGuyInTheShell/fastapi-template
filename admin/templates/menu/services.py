from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.permissions.meta.models import MetaPermissions
from app.modules.users.models import User
from core.database import get_async_db

class MenuService:
    def __init__(self):
        pass

    async def get_menu(self, user: User, session: AsyncSession) -> List[Dict[str, Any]]:
        """
        Generates the sidebar menu for the user based on their permissions and meta data.
        """
        if not user.role or not user.role.permissions:
            return []

        role_permissions_ids = user.role.permissions

        # Fetch all meta permissions related to the user's permissions
        # and filtering for menu specific keys
        stmt = (
            select(MetaPermissions)
            .where(MetaPermissions.ref_permission.in_(role_permissions_ids))
            .where(MetaPermissions.key.startswith("menu_"))
        )
        
        result = await session.execute(stmt)
        meta_items = result.scalars().all()

        # Group meta items by permission ID
        menu_grouped: Dict[int, Dict[str, Any]] = {}
        for meta in meta_items:
            # check attribute name for the ID. Based on model it is ref_permission
            # effectively it is the column holding the FK.
            # However typed as Permission in model, but implies int ID at runtime for the column
            p_id = meta.ref_permission

            if p_id not in menu_grouped:
                menu_grouped[p_id] = {}
            
            # Key format: menu_label, menu_route, menu_icon, menu_order
            clean_key = meta.key.replace("menu_", "", 1)
            menu_grouped[p_id][clean_key] = meta.value

        # Convert to list
        menu_items = []
        for p_id, props in menu_grouped.items():
            # A valid menu item must have at least a label and route
            if "label" in props and "route" in props:
                menu_items.append(props)

        # Sort by 'order' if available, otherwise default to high number
        menu_items.sort(key=lambda x: int(x.get("order", 999)))

        return menu_items
