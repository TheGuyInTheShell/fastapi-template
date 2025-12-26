from sqlalchemy import ForeignKey, Index, String, types

from sqlalchemy.dialects.postgresql import TSVECTOR

from sqlalchemy.orm import Mapped, mapped_column, relationship


from core.database import to_tsvector_ix

from modules.roles.models import Role
from core.database import BaseAsync


class TSVector(types.TypeDecorator):

    impl = TSVECTOR


class User(BaseAsync):

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)

    role_ref: Mapped[str] = mapped_column(
        String, ForeignKey("roles.uid"), nullable=False
    )

    role: Mapped[Role] = relationship("Role")

    password: Mapped[str] = mapped_column(nullable=False)

    email: Mapped[str] = mapped_column(unique=True)

    full_name: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        Index(
            "ix_user_tsv",
            to_tsvector_ix("username", "email", "full_name"),
            postgresql_using="gin",
        ),
        {"extend_existing": True},
    )
