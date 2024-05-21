import datetime
from datetime import date

from pydantic import BaseModel, ConfigDict

from models.user_role import UserRoleEnum


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fio: str
    email: str
    enabled: bool
    role: UserRoleEnum
    type_of_temperature: str
    service_id: int | None
    city_id: int | None


class UserSchemaModel(UserSchema):
    password: str


class UserSchemaAuth(BaseModel):
    email: str
    password: str


class UserSchemaRegister(UserSchemaAuth):
    fio: str


class Services(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    weather_id: int
    service_id: int
    city_id: int
    description: str
    temperature: int
    wind_value: int
    wind_direction: str
    pressure: int
    humidity: int
    date: datetime.datetime
    type: str

    service: dict


class Period(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_date: date
    end_date: date
