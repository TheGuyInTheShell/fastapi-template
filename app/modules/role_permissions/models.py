from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import BaseAsync

class RolePermission(BaseAsync):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships (Optional, but useful)
    role = relationship("app.modules.roles.models.Role", backref="role_permission_entries")
    permission = relationship("app.modules.permissions.models.Permission", backref="role_permission_entries")
