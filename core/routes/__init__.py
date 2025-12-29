from core.utils.import_modules import import_modules

from fastapi import APIRouter, Depends
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY

from core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from core.middlewares.role_verify_cookie import ROLE_VERIFY_COOKIE

from core.event import ChannelEvent
from app.modules.roles.models import Role
from fastapi import HTTPException

channel = ChannelEvent()


api_router = APIRouter()


@api_router.get("/check", dependencies=[])
async def response():
    # channel.emit_to("test").run("test")

    return {"result": "Ok!"}


# Prometheus - Protected metrics endpoint
@api_router.get("/metrics", include_in_schema=False)
async def metrics(
    user=Depends(ROLE_VERIFY_COOKIE),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Prometheus metrics endpoint - protected by authentication and role verification.
    Only accessible to users with owner or observer role.
    """
    # Get allowed role UIDs for metrics access
    # Owner role (level 100) and Observer role (level 50)
    owner_query = await Role.find_by_colunm(db, "name", "owner")
    owner_role = owner_query.scalar_one_or_none()
    
    observer_query = await Role.find_by_colunm(db, "name", "observer")
    observer_role = observer_query.scalar_one_or_none()
    
    # Create set of allowed role UIDs
    allowed_role_uids = set()
    if owner_role:
        allowed_role_uids.add(owner_role.uid)
    if observer_role:
        allowed_role_uids.add(observer_role.uid)
    
    # Check if user's role UID is in the allowed set
    if user.role not in allowed_role_uids:
        raise HTTPException(
            status_code=403,
            detail="Insufficient privileges to access metrics. Only owner and observer roles allowed."
        )
    
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


routes = import_modules(api_router)
