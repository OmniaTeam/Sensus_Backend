from pydantic import BaseModel, ConfigDict

from models.user_role import UserRoleEnum


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fio: str
    email: str
    enabled: bool
    role: UserRoleEnum


class UserSchemaModel(UserSchema):
    password: str


class UserSchemaAuth(BaseModel):
    email: str
    password: str


class UserSchemaRegister(UserSchemaAuth):
    fio: str
