from core.config.globals import settings
from passlib.context import CryptContext  # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.permissions.models import Permission
from app.modules.roles.models import Role
from app.modules.users.models import User



hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OWNER_USER = settings.OWNER_USER
OWNER_EMAIL = settings.OWNER_EMAIL
OWNER_PASS = settings.OWNER_PASS


async def initialize_owner_role(db: AsyncSession) -> Role:
    """
    Creates or retrieves the owner role with all available permissions.
    Owner role has level 100 (highest privilege).

    Returns:
        Role: The owner role instance
    """
    try:
        # Check if owner role already exists
        query = await Role.find_by_colunm(db, "name", "owner")
        owner_role = query.scalar_one_or_none()

        if owner_role:
            print("[v] Owner role already exists")
            return owner_role

        # Get all permissions
        result = await db.execute(select(Permission))
        all_permissions = result.scalars().all()
        permission_ids = [perm.id for perm in all_permissions]

        if not permission_ids:
            print(
                "! Warning: No permissions found. Owner role will be created without permissions."
            )
            permission_ids = []

        # Create owner role
        owner_role = await Role(
            name="owner",
            description="Owner role with full system access",
            level=100,
            permissions=permission_ids,
            disabled=False,
        ).save(db)

        print(f"[v] Created owner role with {len(permission_ids)} permissions")
        return owner_role

    except Exception as e:
        print(f"[x] Error creating owner role: {e}")
        raise e


async def initialize_owner_user(db: AsyncSession, owner_role_id: int) -> User:
    """
    Creates or retrieves the owner user with credentials from environment variables.

    Args:
        db: Database session
        owner_role_id: ID of the owner role

    Returns:
        User: The owner user instance
    """
    try:
        # Check if owner user already exists
        query = await User.find_by_colunm(db, "username", OWNER_USER)
        owner_user = query.scalar_one_or_none()

        if owner_user:
            print(f"[v] Owner user already exists")
            return owner_user

        # Create owner user
        owner_user = await User(
            username=OWNER_USER,
            password=hash_context.hash(OWNER_PASS),
            email=f"{OWNER_EMAIL}",
            full_name="System Owner",
            role_ref=owner_role_id,
        ).save(db)

        print(f"[v] Created owner user")
        return owner_user

    except Exception as e:
        print(f"[x] Error creating owner user: {e}")
        raise e


async def initialize_owner(session_factory: async_sessionmaker[AsyncSession]):
    """
    Main initialization function to create owner role and user.
    Called on app startup.

    Args:
        session_factory: AsyncSession factory to create database sessions
    """
    db: AsyncSession = session_factory()
    try:
        print("\n" + "=" * 50)
        print("Initializing Owner Role and User")
        print("=" * 50)

        # Create/verify owner role
        owner_role = await initialize_owner_role(db)
        role_id = owner_role.id

        # Create/verify owner user
        owner_user = await initialize_owner_user(db, role_id)

        print("=" * 50)
        print("Owner initialization completed successfully")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n[x] Owner initialization failed: {e}\n")
        raise e
    finally:
        await db.close()
