from datetime import datetime
from typing import List

from pydantic import BaseModel


class RQRole(BaseModel):
    name: str
    description: str
    level: int
    permissions: list[str]

class RSRole(BaseModel):
    uid: str
    name: str
    description: str
    level: int
    permissions: list[str]

class RSRoleList(BaseModel):
    data: list[RSRole] | List = []
    total: int = 0
    page: int = 0
    page_size: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
    next_page: int = 0
    prev_page: int = 0