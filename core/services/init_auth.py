from core.services.init_owner import initialize_owner
from core.services.init_subscriber import initialize_subscriber
from core.services.init_observer import initialize_observer
from app.modules.permissions.services import create_permissions_api
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def init_auth(
    permissions_routes: List[Dict[str, Any]], sessionMaker: async_sessionmaker[AsyncSession]
):


    for permission_routes in permissions_routes:
        await create_permissions_api(
            permission_routes["routes"], sessionMaker, permission_routes["type"]
        )
    await initialize_owner(sessionMaker)
    await initialize_subscriber(sessionMaker)
    await initialize_observer(sessionMaker)
