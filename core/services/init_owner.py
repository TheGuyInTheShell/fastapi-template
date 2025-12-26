import os
from typing import List

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.permissions.models import Permission
from modules.roles.models import Role
from modules.users.models import User

load_dotenv()

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OWNER_USER = os.environ.get("OWNER_USER", "admin")
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "admin@admin.com")
OWNER_PASS = os.environ.get("OWNER_PASS", "admin")


async def initialize_owner_role(db: AsyncSession) -> Role:
    """
    Creates or retrieves the owner role with all available permissions.
    Owner role has level 0 (highest privilege).

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
        permission_uids = [perm.uid for perm in all_permissions]

        if not permission_uids:
            print(
                "! Warning: No permissions found. Owner role will be created without permissions."
            )
            permission_uids = []

        # Create owner role
        owner_role = await Role(
            name="owner",
            description="Owner role with full system access",
            level=100,
            permissions=permission_uids,
            disabled=False,
        ).save(db)

        print(f"[v] Created owner role with {len(permission_uids)} permissions")
        return owner_role

    except Exception as e:
        print(f"[x] Error creating owner role: {e}")
        raise e


async def initialize_owner_user(db: AsyncSession, owner_role_uid: str) -> User:
    """
    Creates or retrieves the owner user with credentials from environment variables.

    Args:
        db: Database session
        owner_role_uid: UID of the owner role

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
            role_ref=owner_role_uid,
        ).save(db)

        print(f"[v] Created owner user")
        return owner_user

    except Exception as e:
        print(f"[x] Error creating owner user: {e}")
        raise e


async def initialize_owner(session_factory):
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

        # Create/verify owner user
        owner_user = await initialize_owner_user(db, owner_role.uid)

        print("=" * 50)
        print("Owner initialization completed successfully")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n[x] Owner initialization failed: {e}\n")
        raise e
    finally:
        await db.close()
