from sqlalchemy.ext.asyncio import AsyncSession

from modules.roles.models import Role


async def initialize_subscriber_role(db: AsyncSession) -> Role:
    """
    Creates or retrieves the subscriber role with no permissions.
    Subscriber role has level 100.

    Returns:
        Role: The subscriber role instance
    """
    try:
        # Check if subscriber role already exists
        query = await Role.find_by_colunm(db, "name", "subscriber")
        subscriber_role = query.scalar_one_or_none()

        if subscriber_role:
            print("[v] Subscriber role already exists")
            return subscriber_role

        # Create subscriber role
        subscriber_role = await Role(
            name="subscriber",
            description="Subscriber role with limited access",
            level=0,
            permissions=[],
            disabled=False,
        ).save(db)

        print(f"[v] Created subscriber role")
        return subscriber_role

    except Exception as e:
        print(f"[x] Error creating subscriber role: {e}")
        raise e


async def initialize_subscriber(session_factory):
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
