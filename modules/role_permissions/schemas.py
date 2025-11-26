from pydantic import BaseModel
from typing import List


class RQAssignPermission(BaseModel):
    role_id: str
    permission_id: str


class RQRemovePermission(BaseModel):
    role_id: str
    permission_id: str


class RSPermissionDetail(BaseModel):
    uid: str
    name: str
    action: str
    description: str
    type: str


class RSRolePermissions(BaseModel):
    role_uid: str
    role_name: str
    permissions: List[RSPermissionDetail]
