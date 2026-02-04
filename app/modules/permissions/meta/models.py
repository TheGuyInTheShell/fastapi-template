from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database import BaseAsync
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.modules.permissions.models import Permission


class MetaPermissions(BaseAsync):
    __tablename__ = "meta_permissions"
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    ref_permission: Mapped["Permission"] = mapped_column(ForeignKey("permissions.id"), nullable=False)