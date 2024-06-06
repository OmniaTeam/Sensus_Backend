import copy
import random
from datetime import timedelta, datetime, timezone, time
from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Request, Cookie, Response
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count
from starlette import status
from starlette.responses import RedirectResponse

from api.dependencies import UOWDep, get_user
from models.user_role import UserRoleEnum
from models.models import User, Weather, WeatherService, City, WeatherMonth
from schemas.users import UserSchemaRegister, UserSchemaAuth, UserSchema, Services, Period
from services.auth_service import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, create_token, \
    create_email_token, get_confirm_user, create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
from services.email_service import send_email
from services.users import UserService
from storage.storage import async_session_maker
from utils.logger import logger

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get("/logout")
def delete_cookie(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Cookie deleted!"}


@router.post("/token")
async def login_for_access_token(
        user_register: UserSchemaAuth,
        response: Response,
        uow: UOWDep
):
    user: User = await authenticate_user(uow, user_register.email, user_register.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect usernuow: UOWDep,ame or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    data = {"user_id": user.id}
    response.set_cookie("refresh_token",
                        create_refresh_token(data),
                        httponly=True,
                        expires=datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS),
                        path="/api/users/refresh")

    return


@router.get("/me", response_model=UserSchema)
async def read_users_me(
        current_user: get_user
):
    return UserSchema.model_validate(current_user)


@router.post("/register", status_code=201)
async def register(user_register: UserSchemaRegister, uow: UOWDep):
    logger.info("register")
    user_by_email = await UserService.get_user_by_email(uow, user_register.email)
    if user_by_email:
        if user_by_email.enabled:
            raise HTTPException(status_code=409, detail="User already exists")
        else:
            await UserService.delete_user_by_id(uow, user_by_email.id)
    user_model: User = User(fio=user_register.fio,
                            email=user_register.email,
                            password=get_password_hash(user_register.password),
                            enabled=False,
                            role=UserRoleEnum.user,
                            service_id=1,
                            city_id=1,
                            type_of_temperature="c")

    user_model = await UserService.add_user(uow, user_model)
    email_token = create_email_token(
        data={"user_id": user_model.id})
    send_email(user_register.email, "https://sensus.theomnia.ru/api/users/confirm/" + email_token)
    return UserSchema.model_validate(user_model)


@router.get("/refresh", status_code=200)
async def refresh(uow: UOWDep, response: Response, refresh_token: Annotated[str | None, Cookie()] = None):
    user: User = await get_confirm_user(uow, refresh_token)
    data = {"user_id": user.id}
    response.set_cookie("access_token",
                        create_access_token(data),
                        httponly=True,
                        expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie("refresh_token",
                        create_refresh_token(data),
                        httponly=True,
                        expires=datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS),
                        path="/api/users/refresh")
    return


@router.get("/confirm/{token}", status_code=200)
async def confirm(uow: UOWDep, token: str, request: Request):
    user: User = await get_confirm_user(uow, token)
    async with uow:
        await uow.users.edit_one(user.id, {"enabled": True})
        await uow.commit()
    data = {"user_id": user.id}
    response = RedirectResponse(url=request.base_url, status_code=301)
    response.set_cookie("access_token",
                        create_access_token(data),
                        httponly=True,
                        expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie("refresh_token",
                        create_refresh_token(data),
                        httponly=True,
                        expires=datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS),
                        path="/api/users/refresh")
    return response


@router.get("/weather/now")
async def weather_now(current_user: get_user):
    async with (async_session_maker() as session):
        session: AsyncSession

        stmt = select(Weather).where(
            and_(Weather.city_id == current_user.city_id, Weather.service_id == current_user.service_id,
                 Weather.type == "now")).order_by(Weather.weather_id.desc()).limit(1)
        res = await session.execute(stmt)
        weather = res.scalar_one_or_none()

        if weather is None:
            stmt = select(Weather).where(
                and_(Weather.city_id == current_user.city_id, Weather.service_id == 1,
                     Weather.type == "now")).order_by(Weather.weather_id.desc()).limit(1)
            res = await session.execute(stmt)
            weather = res.scalar_one_or_none()

        return weather


@router.get("/city")
async def get_city(current_user: get_user):
    async with (async_session_maker() as session):
        session: AsyncSession

        stmt = select(City).where(City.city_id == current_user.city_id)
        res = await session.execute(stmt)
        city = res.scalar_one_or_none()

        return city


@router.get("/service")
async def get_service(current_user: get_user):
    async with (async_session_maker() as session):
        session: AsyncSession

        stmt = select(WeatherService).where(WeatherService.service_id == current_user.service_id)
        res = await session.execute(stmt)
        service = res.scalar_one_or_none()

        return service


@router.patch("/temp/{type_temp}")
async def get_service(current_user: get_user, type_temp: str):
    async with (async_session_maker() as session):
        session: AsyncSession

        stmt = select(User).where(User.id == current_user.id)
        res = await session.execute(stmt)
        user: User = res.scalar_one_or_none()
        user.type_of_temperature = type_temp
        await session.commit()
        return


@router.get("/temp_services")
async def get_service(current_user: get_user):
    async with (async_session_maker() as session):
        session: AsyncSession

        stmt = select(WeatherService)
        res = await session.execute(stmt)
        services = res.scalars()
        weathers = []
        for service in services:
            stmt = select(Weather).where(
                and_(Weather.city_id == current_user.city_id, Weather.service_id == service.service_id,
                     Weather.type == "now")).order_by(Weather.weather_id.desc()).limit(1)
            res = await session.execute(stmt)
            weather = res.scalar_one_or_none()
            if weather is None:
                stmt = select(Weather).where(
                    and_(Weather.city_id == current_user.city_id, Weather.service_id == 1,
                         Weather.type == "now")).order_by(Weather.weather_id.desc()).limit(1)
                res = await session.execute(stmt)
                weather = res.scalar_one_or_none()
            weather.service_name = weather.service.name
            weathers.append(weather)

        return weathers

# TODO random
@router.get("/table_stat")
async def get_service(current_user: get_user):
    async with (async_session_maker() as session):
        session: AsyncSession

        stmt = select(WeatherService)
        res = await session.execute(stmt)
        services = res.scalars()
        weathers = []
        for service in services:
            stmt = select(Weather).where(
                and_(Weather.city_id == current_user.city_id, Weather.service_id == service.service_id,
                     Weather.type == "now")).order_by(Weather.weather_id.desc()).limit(1)
            res = await session.execute(stmt)
            weather = res.scalar_one_or_none()

            if weather is None:
                stmt = select(Weather).where(
                    and_(Weather.city_id == current_user.city_id, Weather.service_id == 1,
                         Weather.type == "now")).order_by(Weather.weather_id.desc()).limit(1)
                res = await session.execute(stmt)
                weather = res.scalar_one_or_none()

                weather = copy.deepcopy(weather)
                weather.service_id = service.service_id
                weather.humidity = randomize_integer(weather.humidity)
                weather.temperature = randomize_integer(weather.temperature)
                weather.pressure = randomize_integer(weather.pressure)
                weather.wind_value = randomize_integer(weather.wind_value)
                weather.wind_direction = random_string_from_list()



            if weather is not None:


                weather.service_name = service.name
                stmt = select(count(User.id)).where(User.service_id == service.service_id)
                user_count = await session.execute(stmt)
                user_count = int(user_count.scalar_one_or_none())
                weather.user_count = user_count
                weathers.append(weather)

        return weathers


@router.get("/weather/today")
async def get_weather_today(current_user: get_user):
    async with (async_session_maker() as session):
        session: AsyncSession
        current_date = datetime.now().date()

        # Начальная дата - начало текущего дня (00:00:00)
        start_date = datetime.combine(current_date, time.min)

        # Конечная дата - конец текущего дня (23:59:59)
        end_date = datetime.combine(current_date, time.max)
        stmt = select(Weather).limit(8).filter(
            Weather.service_id == current_user.service_id,
            Weather.city_id == current_user.city_id,
            Weather.date >= start_date,
            Weather.date <= end_date,
            Weather.type == "today"
        )
        res = await session.execute(stmt)
        weathers = [row for row in res.scalars()]

        if weathers == []:
            stmt = select(Weather).limit(8).filter(
                Weather.service_id == 1,
                Weather.city_id == current_user.city_id,
                Weather.date >= start_date,
                Weather.date <= end_date,
                Weather.type == "today"
            )
            res = await session.execute(stmt)
            weathers = [row for row in res.scalars()]

        return weathers


@router.get("/weather/days")
async def get_weather_today(current_user: get_user):
    async with (async_session_maker() as session):
        session: AsyncSession
        current_date = datetime.now()
        # Начальная дата - начало текущего дня (00:00:00)
        start_date = datetime.combine(current_date, time.min)
        ten_days = current_date + timedelta(days=10)

        end_date = datetime.combine(ten_days, time.max)
        stmt = select(Weather).limit(10).filter(
            Weather.service_id == current_user.service_id,
            Weather.city_id == current_user.city_id,
            Weather.date >= start_date,
            Weather.date <= end_date,
            Weather.type == "days"
        )
        res = await session.execute(stmt)
        weathers = [row for row in res.scalars()]

        if weathers == []:
            stmt = select(Weather).limit(10).filter(
                Weather.service_id == current_user.service_id,
                Weather.city_id == current_user.city_id,
                Weather.date >= start_date,
                Weather.date <= end_date,
                Weather.type == "days"
            )
            res = await session.execute(stmt)
            weathers = [row for row in res.scalars()]
        return weathers


@router.get("/cities")
async def get_cities():
    async with (async_session_maker() as session):
        stmt = select(City)
        res = await session.execute(stmt)
        cities = res.scalars().all()
    return cities


# Получение всех сервисов погоды
@router.get("/services")
async def get_services():
    async with (async_session_maker() as session):
        stmt = select(WeatherService)
        res = await session.execute(stmt)
        services = res.scalars().all()
    return services


@router.put("/update")
async def update_user(city_id: int, service_id: int, current_user: get_user):
    async with (async_session_maker() as session):
        # Проверяем существование пользователя
        stmt = select(User).filter(User.id == current_user.id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Обновляем данные пользователя
        user.city_id = city_id
        user.service_id = service_id
        await session.commit()

    return


@router.post("/weather_data")
async def get_weather_data_for_period(period: Period):
    async with async_session_maker() as session:
        stmt = select(WeatherMonth).where(
            WeatherMonth.date.between(period.start_date, period.end_date)
        )
        res = await session.execute(stmt)
        weather_data = res.scalars().all()

        if not weather_data:
            raise HTTPException(status_code=404, detail="No data found for the specified period")

    return weather_data

def randomize_integer(number):
    random_offset = random.randint(0, 2)  # Генерируем случайное смещение от -2 до 2
    new_number = number + random_offset
    return new_number

def random_string_from_list():
    string_list = ["С", "Ю", "З", "В", "C/З"]
    return random.choice(string_list)
