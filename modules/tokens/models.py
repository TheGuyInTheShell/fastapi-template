from datetime import datetime

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import BaseAsync
from modules.roles.models import Role


class ApiToken(BaseAsync):
    __tablename__ = "api_tokens"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    role_ref: Mapped[str] = mapped_column(
        String, ForeignKey("roles.uid"), nullable=False
    )
    role: Mapped[Role] = relationship("Role")
    expiration: Mapped[datetime] = mapped_column(Date)
