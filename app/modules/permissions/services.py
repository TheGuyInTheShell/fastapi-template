from typing import List, Callable

from fastapi.routing import APIRoute, BaseRoute
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import Permission
from sqlalchemy import select


async def create_permissions_api(
    routes: List[BaseRoute], sessionAsync: async_sessionmaker[AsyncSession], type: str
):
    db: AsyncSession = sessionAsync()
    try:

        api_routes = [route for route in routes if isinstance(route, APIRoute)]
        if not api_routes:
            return

        # Collect all permission names to check in bulk
        permission_names = [route.name for route in api_routes]

        # Find existing permissions in bulk
        result = await db.execute(
            select(Permission.name).where(Permission.name.in_(permission_names))
        )
        existing_names = {row[0] for row in result.all()}

        new_permissions = []
        for route in api_routes:
            name: str = route.name
            if name not in existing_names:
                methods: set = route.methods
                description: str = route.path
                new_permissions.append(
                    Permission(
                        name=name,
                        action=next(iter(methods)) if methods else "UNKNOWN",
                        description=description,
                        type=type,
                    )
                )

        if new_permissions:
            db.add_all(new_permissions)
            await db.commit()
            print(f"Created {len(new_permissions)} new permissions of type '{type}'")
        else:
            print(f"No new permissions to create for type '{type}'")

    except Exception as e:
        print(f"Error in create_permissions_api: {e}")
    finally:
        await db.close()
