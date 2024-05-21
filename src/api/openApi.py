from datetime import datetime, time, timedelta

from fastapi import APIRouter
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Weather
from storage.storage import async_session_maker

router = APIRouter(
    prefix="",
    tags=["open api"],
)

@router.get("/weather/now")
async def weather_now():
    async with (async_session_maker() as session):
        session: AsyncSession

        stmt = select(Weather).where(
            and_(Weather.city_id == 1, Weather.service_id == 1,
                 Weather.type == "now")).order_by(Weather.weather_id.desc()).limit(1)
        res = await session.execute(stmt)
        weather = res.scalar_one_or_none()

        return weather


@router.get("/weather/today")
async def get_weather_today():
    async with (async_session_maker() as session):
        session: AsyncSession
        current_date = datetime.now().date()

        # Начальная дата - начало текущего дня (00:00:00)
        start_date = datetime.combine(current_date, time.min)

        # Конечная дата - конец текущего дня (23:59:59)
        end_date = datetime.combine(current_date, time.max)
        stmt = select(Weather).limit(8).filter(
            Weather.service_id == 1,
            Weather.city_id == 1,
            Weather.date >= start_date,
            Weather.date <= end_date,
            Weather.type == "today"
        )
        res = await session.execute(stmt)
        weathers = [row for row in res.scalars()]

        return weathers


@router.get("/weather/days")
async def get_weather_today():
    async with (async_session_maker() as session):
        session: AsyncSession
        current_date = datetime.now()
        # Начальная дата - начало текущего дня (00:00:00)
        start_date = datetime.combine(current_date, time.min)
        ten_days = current_date + timedelta(days=10)

        end_date = datetime.combine(ten_days, time.max)
        stmt = select(Weather).limit(10).filter(
            Weather.service_id == 1,
            Weather.city_id == 1,
            Weather.date >= start_date,
            Weather.date <= end_date,
            Weather.type == "days"
        )
        res = await session.execute(stmt)
        weathers = [row for row in res.scalars()]

        return weathers