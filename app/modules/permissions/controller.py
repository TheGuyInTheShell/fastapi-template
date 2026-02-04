from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_db
from core import cache

from .models import Permission
from .schemas import (
    RQPermission, 
    RQCreatePermission,
    RQBulkPermissions,
    RSPermission, 
    RSPermissionList,
    RSBulkPermissionsResponse
)
from .services import create_permission, create_bulk_permissions_with_roles

# prefix /permissions
router = APIRouter()

tag = "permissions"


@router.get("/id/{id}", response_model=RSPermission, status_code=200, tags=[tag])
async def get_Permission(
    id: str, db: AsyncSession = Depends(get_async_db)
) -> RSPermission:
    try:
        result: Permission = await Permission.find_one(db, id)
        return RSPermission(
            uid=result.uid,
            id=result.id,
            action=result.action,
            description=result.description,
            name=result.name,
            type=result.type,
        )
    except Exception as e:
        print(e)
        raise e


@router.get("/", response_model=RSPermissionList, status_code=200, tags=[tag])
async def get_Permissions(
    pag: Optional[int] = 1,
    ord: Literal["asc", "desc"] = "asc",
    status: Literal["deleted", "exists", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RSPermissionList:
    try:
        result = await Permission.find_some(db,  pag or 1, ord, status)
        result2 = list(map(
            lambda x: RSPermission(
                uid=x.uid,
                id=x.id,
                action=x.action,
                description=x.description,
                name=x.name,
                type=x.type,
            ),
            result,
        ))
        return RSPermissionList(
            data=result2,
            total=0,
            page=0,
            page_size=0,
            total_pages=0,
            has_next=False,
            has_prev=False,
            next_page=0,
            prev_page=0,
        )
    except Exception as e:
        print(e)
        raise e


@router.get("/all", response_model=RSPermissionList, status_code=200, tags=[tag])
@cache.cache_endpoint(ttl=60, namespace="permissions")
async def get_all_Permissions(
    status: Literal["deleted", "exists", "all"] = "exists",
    db: AsyncSession = Depends(get_async_db),
) -> RSPermissionList:
    try:
        result = await Permission.find_all(db, status)
        result2 = list(map(
            lambda x: RSPermission(
                uid=x.uid,
                id=x.id,
                action=x.action,
                description=x.description,
                name=x.name,
                type=x.type,
            ),
            result,
        ))
        return RSPermissionList(
            data=result2,
            total=len(result),
            page=0,
            page_size=0,
            total_pages=0,
            has_next=False,
            has_prev=False,
            next_page=0,
            prev_page=0,
        )
    except Exception as e:
        print(e)
        raise e


@router.post("/", response_model=RSPermission, status_code=201, tags=[tag])
async def create_Permission(
    permission: RQPermission, db: AsyncSession = Depends(get_async_db)
) -> RSPermission:
    try:
        result = await Permission(**permission.model_dump()).save(db)
        return result
    except Exception as e:
        print(e)
        raise e


@router.delete("/id/{id}", status_code=204, tags=[tag])
async def delete_Permission(id: str, db: AsyncSession = Depends(get_async_db)) -> None:
    try:
        await Permission.delete(db, id)
    except Exception as e:
        print(e)
        raise e


@router.put("/id/{id}", response_model=RSPermission, status_code=200, tags=[tag])
async def update_Permission(
    id: str, permission: RQPermission, db: AsyncSession = Depends(get_async_db)
) -> RSPermission:
    try:
        result = await Permission.update(db, id, permission.model_dump())
        return result
    except Exception as e:
        print(e)
        raise e


@router.post("/bulk", response_model=RSBulkPermissionsResponse, status_code=201, tags=[tag])
async def create_bulk_permissions(
    bulk_data: RQBulkPermissions, 
    db: AsyncSession = Depends(get_async_db)
) -> RSBulkPermissionsResponse:
    """
    Crea múltiples permisos en bulk y los asigna a sus roles correspondientes.
    
    Args:
        bulk_data: Datos de los permisos a crear con sus roles asociados
        db: Sesión de base de datos
        
    Returns:
        RSBulkPermissionsResponse: Resultado de la creación en bulk
        
    Example:
        ```json
        {
            "permissions": [
                {
                    "name": "create_user",
                    "action": "POST",
                    "description": "/api/users",
                    "type": "api",
                    "role_id": "uuid-del-rol"
                },
                {
                    "name": "delete_user",
                    "action": "DELETE",
                    "description": "/api/users/{id}",
                    "type": "api",
                    "role_id": "uuid-del-rol"
                }
            ]
        }
        ```
    """
    try:
        results, success_count, error_count = await create_bulk_permissions_with_roles(
            db=db,
            permissions_data=bulk_data.permissions
        )
        
        return RSBulkPermissionsResponse(
            created=results,
            total=len(bulk_data.permissions),
            success_count=success_count,
            error_count=error_count
        )
    except Exception as e:
        print(f"Error in create_bulk_permissions endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear permisos en bulk: {str(e)}"
        )
