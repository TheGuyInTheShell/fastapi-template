from core.services.init_owner import initialize_owner
from core.services.init_subscriber import initialize_subscriber
from modules.permissions.services import create_permissions_api
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession


async def init_auth(
    permissions_routes: List[Dict[str, Any]], sessionAsync: AsyncSession
):
    for permission_routes in permissions_routes:
        await create_permissions_api(
            permission_routes["routes"], sessionAsync, permission_routes["type"]
        )
    await initialize_owner(sessionAsync)
    await initialize_subscriber(sessionAsync)
