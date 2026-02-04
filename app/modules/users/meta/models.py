from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database import BaseAsync
from app.modules.users.models import User

class MetaUsers(BaseAsync):
    __tablename__ = "meta_users"
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    ref_user: Mapped[User] = mapped_column(ForeignKey("users.id"))
