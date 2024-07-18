from typing import List
from pydantic import BaseModel


class RQMenuRole(BaseModel):
    name: str
    description: str
    level: int
    menus: List[str]
    disabled: bool = False


class RSMenuRole(BaseModel):
    uid: str
    name: str
    description: str
    level: int
    menus: List[str]
    disabled: bool = False


class RSMenuRoleList(BaseModel):
    data: list[RSMenuRole] | List = []
    total: int = 0
    page: int = 0
    page_size: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
    next_page: int = 0
    prev_page: int = 0