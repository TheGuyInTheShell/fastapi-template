from typing import List, Callable

from fastapi.routing import APIRoute, BaseRoute
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import Permission
from .schemas import RQCreatePermission, RQBulkPermission, RSPermission, RSBulkPermissionResult
from app.modules.roles.models import Role
from app.modules.role_permissions.models import RolePermission
from sqlalchemy import select


async def create_permission(
    db: AsyncSession,
    name: str,
    action: str,
    description: str,
    type: str
) -> Permission:
    """
    Crea un solo permiso en la base de datos.
    
    Args:
        db: Sesión de base de datos
        name: Nombre del permiso
        action: Acción del permiso (GET, POST, PUT, DELETE, etc.)
        description: Descripción del permiso
        type: Tipo del permiso (api, admin, etc.)
        
    Returns:
        Permission: El permiso creado
        
    Raises:
        Exception: Si hay un error al crear el permiso
    """
    permission = Permission(
        name=name,
        action=action,
        description=description,
        type=type,
    )
    await permission.save(db)
    return permission


async def create_bulk_permissions_with_roles(
    db: AsyncSession,
    permissions_data: List[RQBulkPermission]
) -> tuple[List[RSBulkPermissionResult], int, int]:
    """
    Crea múltiples permisos y los asigna a sus roles correspondientes.
    
    Args:
        db: Sesión de base de datos
        permissions_data: Lista de permisos a crear con sus roles asociados
        
    Returns:
        tuple: (resultados, total_exitosos, total_errores)
            - resultados: Lista de RSBulkPermissionResult con el resultado de cada creación
            - total_exitosos: Número de permisos creados exitosamente
            - total_errores: Número de errores durante la creación
    """
    results: List[RSBulkPermissionResult] = []
    success_count = 0
    error_count = 0
    
    for perm_data in permissions_data:
        try:
            # Verificar si el permiso ya existe
            existing_query = await db.execute(
                select(Permission).where(Permission.name == perm_data.name)
            )
            existing_permission = existing_query.scalar_one_or_none()
            
            if existing_permission:
                # Si ya existe, usamos el existente
                permission = existing_permission
            else:
                # Crear el nuevo permiso
                permission = await create_permission(
                    db=db,
                    name=perm_data.name,
                    action=perm_data.action,
                    description=perm_data.description,
                    type=perm_data.type
                )
            
            # Verificar que el rol existe
            role = await Role.find_one(db, perm_data.role_id)
            
            # Asignar el permiso al rol si no está ya asignado
            if permission.id not in role.permissions:
                updated_permissions = list(role.permissions) + [permission.id]
                await role.update(db, perm_data.role_id, {"permissions": updated_permissions})
            
            # Sync Pivot Table (RolePermission)
            permission_id = permission.id
            rp_query = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == perm_data.role_id,
                    RolePermission.permission_id == permission_id
                )
            )
            if not rp_query.scalar_one_or_none():
                await RolePermission(
                    role_id=perm_data.role_id,
                    permission_id=permission_id
                ).save(db)
            
            # Agregar resultado exitoso
            results.append(RSBulkPermissionResult(
                permission=RSPermission(
                    id=permission.id,
                    uid=permission.uid,
                    type=permission.type,
                    name=permission.name,
                    action=permission.action,
                    description=permission.description,
                ),
                role_id=perm_data.role_id,
                success=True,
                error=None
            ))
            success_count += 1
            
        except Exception as e:
            # Agregar resultado con error
            results.append(RSBulkPermissionResult(
                permission=RSPermission(
                    id=0,
                    uid="",
                    type=perm_data.type,
                    name=perm_data.name,
                    action=perm_data.action,
                    description=perm_data.description,
                ),
                role_id=perm_data.role_id,
                success=False,
                error=str(e)
            ))
            error_count += 1
    
    return results, success_count, error_count


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
