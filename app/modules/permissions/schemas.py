from datetime import datetime
from typing import List

from pydantic import BaseModel


class RQPermission(BaseModel):
    name: str
    description: str


class RQCreatePermission(BaseModel):
    """Schema para crear un permiso individual"""
    name: str
    action: str
    description: str
    type: str


class RQBulkPermission(BaseModel):
    """Schema para crear un permiso dentro de un bulk"""
    name: str
    action: str
    description: str
    type: str
    role_id: str


class RQBulkPermissions(BaseModel):
    """Schema para crear múltiples permisos con sus roles asociados"""
    permissions: List[RQBulkPermission]


class RSPermission(BaseModel):
    uid: str
    type: str
    name: str
    action: str
    description: str


class RSBulkPermissionResult(BaseModel):
    """Schema para el resultado de la creación de un permiso en bulk"""
    permission: RSPermission
    role_id: str
    success: bool
    error: str | None = None


class RSBulkPermissionsResponse(BaseModel):
    """Schema para la respuesta de creación en bulk"""
    created: List[RSBulkPermissionResult]
    total: int
    success_count: int
    error_count: int


class RSPermissionList(BaseModel):
    data: list[RSPermission] | List = []
    total: int = 0
    page: int | None = 0
    page_size: int | None = 0
    total_pages: int | None = 0
    has_next: bool | None = False
    has_prev: bool | None = False
    next_page: int | None = 0
    prev_page: int | None = 0
