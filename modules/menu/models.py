from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import BaseAsync


class Menu(BaseAsync):
    __tablename__ = "menu"
    
    name: Mapped[str] = mapped_column(nullable=False)
    type_menu: Mapped[str] = mapped_column(nullable=False)
    file_route: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False)

