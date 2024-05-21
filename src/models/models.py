from sqlalchemy import Enum, Column, Integer, ForeignKey, String, Boolean, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.user_role import UserRoleEnum
from schemas.users import UserSchema

from storage.storage import Base


# class Users(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     fio: Mapped[str]
#     email: Mapped[str] = mapped_column(unique=True)
#     password: Mapped[str]
#     enabled: Mapped[bool]
#     role = Column(Enum(UserRoleEnum))
#


# class City(Base):
#     __tablename__ = 'city'
#     city_id = Column(Integer, primary_key=True)
#     city_name = Column(String(255))
#
#     weather_services = relationship("WeatherService", back_populates="city")
#
#
# class User(Base):
#     __tablename__ = 'user'
#     id = Column(Integer, primary_key=True)
#     service_id = Column(Integer, ForeignKey('weather_service.service_id'))
#     city_id = Column(Integer, ForeignKey('weather_service.service_id'))
#     fio = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False)
#     password = Column(String(255), nullable=False)
#     role = Column(Enum(UserRoleEnum))
#     enabled = Column(Boolean, nullable=False)
#     type_of_temperature = Column(String(255), nullable=False)
#
#     service = relationship("WeatherService")
#

#
#
# class Weather(Base):
#     __tablename__ = 'weather'
#     weather_id = Column(Integer, primary_key=True)
#     service_id = Column(Integer, ForeignKey('weather_service.service_id'))
#     description = Column(String(255), nullable=False)
#     temperature = Column(Integer, nullable=False)
#     wind_value = Column(Integer)
#     wind_direction = Column(String(255))
#     pressure = Column(Integer)
#     humidity = Column(Integer)
#     date = Column(DateTime, nullable=False)
#     type = Column(String(255), nullable=False)
#
#     service = relationship("WeatherService")
#
#
# class WeatherMonth(Base):
#     __tablename__ = 'weather_month'
#     month_id = Column(Integer, primary_key=True)
#     city_id = Column(Integer, ForeignKey('city.city_id'))
#     max_temp = Column(Integer)
#     min_temp = Column(Integer)
#     average_temp = Column(Integer)
#     average_wind = Column(Integer)
#     date = Column(Date)
#
#     city = relationship("City")
#
#
# class WeatherService(Base):
#     __tablename__ = 'weather_service'
#     service_id = Column(Integer, primary_key=True)
#     city_id = Column(Integer, ForeignKey('city.city_id'))
#     name = Column(String(255), nullable=False)
#     url = Column(String(255))
#
#     city = relationship("City", back_populates="weather_services")

class City(Base):
    __tablename__ = 'City'

    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(255))

    users = relationship("User", back_populates="city")
    weathers = relationship("Weather", back_populates="city")
    weather_months = relationship("WeatherMonth", back_populates="city")


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('weather_service.service_id'))
    city_id = Column(Integer, ForeignKey('City.city_id'))
    fio = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum))
    enabled = Column(Boolean, nullable=False)
    type_of_temperature = Column(String(255), nullable=False)

    city = relationship("City", back_populates="users")

    def to_read_model(self) -> UserSchema:
        return UserSchema(
            id=self.id,
            fio=self.fio,
            email=self.email,
            role=self.role,
            service_id=self.service_id,
            enabled=self.enabled,
            type_of_tempreture=self.type_of_temperature
        )


class WeatherMonth(Base):
    __tablename__ = 'weather_month'

    month_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('City.city_id'))
    average_temp = Column(Integer)
    average_wind = Column(Integer)
    date = Column(Date)

    city = relationship("City", back_populates="weather_months")


class WeatherService(Base):
    __tablename__ = 'weather_service'

    service_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    weathers = relationship("Weather", back_populates="service")


class Weather(Base):
    __tablename__ = 'weather'

    weather_id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('weather_service.service_id'))
    city_id = Column(Integer, ForeignKey('City.city_id'))
    description = Column(String(255), nullable=False)
    temperature = Column(Integer, nullable=False)
    wind_value = Column(Integer)
    wind_direction = Column(String(255))
    pressure = Column(Integer)
    humidity = Column(Integer)
    date = Column(DateTime, nullable=False)
    type = Column(String(255), nullable=False)

    city = relationship("City", back_populates="weathers")
    service = relationship("WeatherService", back_populates="weathers")
