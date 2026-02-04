from sqlalchemy import ForeignKey, Index, Integer, String, types

from sqlalchemy.dialects.postgresql import TSVECTOR

from sqlalchemy.orm import Mapped, mapped_column, relationship


from core.database import to_tsvector_ix

from app.modules.roles.models import Role
from core.database import BaseAsync


class TSVector(types.TypeDecorator):

    impl = TSVECTOR


class User(BaseAsync):

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)

    role_ref: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False
    )

    role: Mapped[Role] = relationship("Role")

    password: Mapped[str] = mapped_column(nullable=False)

    email: Mapped[str] = mapped_column(unique=True)

    full_name: Mapped[str] = mapped_column(nullable=False)

    otp_secret: Mapped[str] = mapped_column(String, nullable=True)
    otp_enabled: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        Index(
            "ix_user_tsv",
            to_tsvector_ix("username", "email", "full_name"),
            postgresql_using="gin",
        ),
        {"extend_existing": True},
    )
