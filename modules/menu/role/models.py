from sqlalchemy.orm import Mapped, mapped_column
from core.database.base import BaseAsync
from sqlalchemy import ARRAY, String, Integer, Boolean
from typing import List


class MenuRole(BaseAsync):
    __tablename__ = "menu_role"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    menus: Mapped[List[ModuleNotFoundError]] = mapped_column(ARRAY(String, as_tuple=True), nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
