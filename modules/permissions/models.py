from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import BaseAsync


class Permission(BaseAsync):
    __tablename__ = "permissions"
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)