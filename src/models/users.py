from sqlalchemy import Enum, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column


from models.user_role import UserRoleEnum
from schemas.users import UserSchema

from storage.storage import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fio: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    disabled: Mapped[bool]
    role = Column(Enum(UserRoleEnum))

    def to_read_model(self) -> UserSchema:
        return UserSchema(
            id=self.id,
            fio=self.fio,
            email=self.email,
            role=self.role
        )
