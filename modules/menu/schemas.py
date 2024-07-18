from typing import List

from pydantic import BaseModel


class RQMenu(BaseModel):
    name: str
    type_menu: str
    file_route: str
    active: bool = True


class RSMenu(BaseModel):
    uid: str
    name: str
    type_menu: str
    file_route: str
    active: bool

class RSMenuList(BaseModel):
    data: list[RSMenu] | List = []
    total: int = 0
    page: int = 0
    page_size: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
    next_page: int = 0
    prev_page: int = 0