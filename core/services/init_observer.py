from core.config.globals import settings
from passlib.context import CryptContext # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.permissions.models import Permission
from app.modules.roles.models import Role
from app.modules.users.models import User
from app.modules.role_permissions.models import RolePermission


hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OBSERVER_USER = settings.OBSERVER_USER
OBSERVER_EMAIL = settings.OBSERVER_EMAIL
OBSERVER_PASS = settings.OBSERVER_PASS


async def initialize_observer_role(db: AsyncSession) -> Role:
    """
    Creates or retrieves the observer role with minimal permissions.
    Observer role can only view metrics (level 50).

    Returns:
        Role: The observer role instance
    """
    try:
        # Check if observer role already exists
        query = await Role.find_by_colunm(db, "name", "observer")
        observer_role = query.scalar_one_or_none()

        if not observer_role:
            # Observer role has no permissions - only metrics access controlled separately
            # Level 50 is below owner (100) but above subscriber
            
            observer_role = await Role(
                name="observer",
                description="Observer role with metrics access only",
                level=50,
                permissions=[],  # No standard route permissions
                disabled=False,
            ).save(db)

            print(f"[v] Created observer role (metrics access only)")
        else:
            print("[v] Observer role already exists")

        # Sync Pivot Table (RolePermission)
        observer_role_id = observer_role.id
        permission_ids = observer_role.permissions
        for perm_id in permission_ids:
            rp_query = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == observer_role_id,
                    RolePermission.permission_id == perm_id
                )
            )
            if not rp_query.scalar_one_or_none():
                await RolePermission(
                    role_id=observer_role_id,
                    permission_id=perm_id
                ).save(db)

        if permission_ids:
            print(f"[v] Synced observer role permissions in pivot table")

        return observer_role

    except Exception as e:
        print(f"[x] Error creating observer role: {e}")
        raise e


async def initialize_observer_user(db: AsyncSession, observer_role_id: int) -> User:
    """
    Creates or retrieves the observer user with credentials from environment variables.

    Args:
        db: Database session
        observer_role_id: ID of the observer role

    Returns:
        User: The observer user instance
    """
    try:
        # Check if observer user already exists
        query = await User.find_by_colunm(db, "username", OBSERVER_USER)
        observer_user = query.scalar_one_or_none()

        if observer_user:
            print(f"[v] Observer user already exists")
            return observer_user

        # Create observer user
        observer_user = await User(
            username=OBSERVER_USER,
            password=hash_context.hash(OBSERVER_PASS),
            email=f"{OBSERVER_EMAIL}",
            full_name="System Observer",
            role_ref=observer_role_id,
        ).save(db)

        print(f"[v] Created observer user")
        return observer_user

    except Exception as e:
        print(f"[x] Error creating observer user: {e}")
        raise e


async def initialize_observer(session_factory: async_sessionmaker[AsyncSession]):
    """
    Main initialization function to create observer role and user.
    Called on app startup.

    Args:
        session_factory: AsyncSession factory to create database sessions
    """
    db: AsyncSession = session_factory()
    try:
        print("\n" + "=" * 50)
        print("Initializing Observer Role and User")
        print("=" * 50)

        # Create/verify observer role
        observer_role = await initialize_observer_role(db)
        role_id = observer_role.id

        # Create/verify observer user
        observer_user = await initialize_observer_user(db, role_id)

        print("=" * 50)
        print("Observer initialization completed successfully")
        print("=" * 50 + "\n")
        
        return role_id  # Return the ID for metrics verification

    except Exception as e:
        print(f"\n[x] Observer initialization failed: {e}\n")
        raise e
    finally:
        await db.close()
