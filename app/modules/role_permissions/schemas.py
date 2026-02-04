from pydantic import BaseModel
from typing import List


class RQAssignPermission(BaseModel):
    role_id: int
    permission_id: int


class RQRemovePermission(BaseModel):
    role_id: int
    permission_id: int


class RSPermissionDetail(BaseModel):
    id: int
    name: str
    action: str
    description: str
    type: str


class RSRolePermissions(BaseModel):
    role_id: int
    role_name: str
    permissions: List[RSPermissionDetail]
