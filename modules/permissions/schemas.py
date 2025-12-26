from datetime import datetime
from typing import List

from pydantic import BaseModel


class RQPermission(BaseModel):
    name: str
    description: str


class RSPermission(BaseModel):
    uid: str
    type: str
    name: str
    action: str
    description: str


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
