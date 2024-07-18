from datetime import datetime
from typing import List

from pydantic import BaseModel


class RQApiToken(BaseModel):
    name: str
    description: str
    duration: int | None
    role_ref: str


class RSApiToken(BaseModel):
    uid: str
    name: str
    description: str
    duration: datetime | None
    role_ref: str


class RSApiTokensList(BaseModel):
    data: list[RSApiToken] | List = []
    total: int = 0
    page: int = 0
    page_size: int = 0
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
    next_page: int = 0
    prev_page: int = 0
