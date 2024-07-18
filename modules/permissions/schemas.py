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
    page: int = 0
    page_size: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
    next_page: int = 0
    prev_page: int = 0