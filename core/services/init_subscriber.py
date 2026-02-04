from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.roles.models import Role
from app.modules.role_permissions.models import RolePermission


async def initialize_subscriber_role(db: AsyncSession) -> Role:
    """
    Creates or retrieves the subscriber role with no permissions.
    Subscriber role has level 0 (lowest privilege).

    Returns:
        Role: The subscriber role instance
    """
    try:
        # Check if subscriber role already exists
        query = await Role.find_by_colunm(db, "name", "subscriber")
        subscriber_role = query.scalar_one_or_none()

        if not subscriber_role:
            # Create subscriber role
            subscriber_role = await Role(
                name="subscriber",
                description="Subscriber role with limited access",
                level=0,
                permissions=[],
                disabled=False,
            ).save(db)

            print(f"[v] Created subscriber role")
        else:
            print("[v] Subscriber role already exists")

        # Sync Pivot Table (RolePermission)
        subscriber_role_id = subscriber_role.id
        permission_ids = subscriber_role.permissions
        for perm_id in permission_ids:
            rp_query = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == subscriber_role_id,
                    RolePermission.permission_id == perm_id
                )
            )
            if not rp_query.scalar_one_or_none():
                await RolePermission(
                    role_id=subscriber_role_id,
                    permission_id=perm_id
                ).save(db)

        if permission_ids:
            print(f"[v] Synced subscriber role permissions in pivot table")

        return subscriber_role

    except Exception as e:
        print(f"[x] Error creating subscriber role: {e}")
        raise e


async def initialize_subscriber(session_factory: async_sessionmaker[AsyncSession]):
    """
    Main initialization function to create subscriber role.
    Called on app startup.

    Args:
        session_factory: AsyncSession factory to create database sessions
    """
    db: AsyncSession = session_factory()
    try:
        print("\n" + "=" * 50)
        print("Initializing Subscriber Role")
        print("=" * 50)

        # Create/verify subscriber role
        await initialize_subscriber_role(db)

        print("=" * 50)
        print("Subscriber initialization completed successfully")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n[x] Subscriber initialization failed: {e}\n")
        raise e
    finally:
        await db.close()
