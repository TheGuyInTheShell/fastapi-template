from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.modules.roles.models import Role
from app.modules.permissions.models import Permission
from .schemas import RSPermissionDetail, RSRolePermissions


async def assign_permission_to_role(
    db: AsyncSession, role_id: str, permission_id: str
) -> Role:
    """
    Assigns a permission to a role by adding the permission UID to the role's permissions array.

    Args:
        db: Database session
        role_id: UID of the role
        permission_id: UID of the permission

    Returns:
        Updated Role object
    """
    # Get the role
    role = await Role.find_one(db, role_id)

    # Get the permission to verify it exists
    permission = await Permission.find_one(db, permission_id)

    # Add permission UID to role's permissions array if not already present
    if permission.uid not in role.permissions:
        updated_permissions = list(role.permissions) + [permission.uid]
        await role.update(db, role_id, {"permissions": updated_permissions})

    return role


async def remove_permission_from_role(
    db: AsyncSession, role_id: str, permission_id: str
) -> Role:
    """
    Removes a permission from a role by removing the permission UID from the role's permissions array.

    Args:
        db: Database session
        role_id: UID of the role
        permission_id: UID of the permission

    Returns:
        Updated Role object
    """
    # Get the role
    role = await Role.find_one(db, role_id)

    # Remove permission UID from role's permissions array if present
    if permission_id in role.permissions:
        updated_permissions = [p for p in role.permissions if p != permission_id]
        await role.update(db, role_id, {"permissions": updated_permissions})

    return role


async def get_role_permissions(db: AsyncSession, role_id: str) -> RSRolePermissions:
    """
    Gets all permissions for a role, returning full Permission objects.

    Args:
        db: Database session
        role_id: UID of the role

    Returns:
        RSRolePermissions object with role info and list of permissions
    """
    # Get the role
    role = await Role.find_one(db, role_id)

    # Get all permissions for this role
    permissions = []
    for permission_uid in role.permissions:
        try:
            permission = await Permission.find_one(db, permission_uid)
            permissions.append(
                RSPermissionDetail(
                    uid=permission.uid,
                    name=permission.name,
                    action=permission.action,
                    description=permission.description,
                    type=permission.type,
                )
            )
        except:
            # Skip permissions that no longer exist
            continue

    return RSRolePermissions(
        role_uid=role.uid, role_name=role.name, permissions=permissions
    )
