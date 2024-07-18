from typing import List

from sqlalchemy import ARRAY, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import BaseAsync


class Role(BaseAsync):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    permissions: Mapped[List[str]] = mapped_column(ARRAY(String, as_tuple=True), nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)