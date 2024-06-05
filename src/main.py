import asyncio

import uvicorn
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, APIRouter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from api.routers import all_routers
from parser.gismetio import *

app = FastAPI(
    title="Sensus Weather",
    debug=True,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)
main_router = APIRouter(prefix="/api")

for router in all_routers:
    main_router.include_router(router)

app.include_router(main_router)

async def job1():
    await gismetio_lipetsk_now()
    await asyncio.sleep(1)
    await gismetio_dankov_now()
    await asyncio.sleep(1)
    await gismetio_yelets_now()
    await asyncio.sleep(1)
    await gismetio_gryzi_now()
    await asyncio.sleep(1)
    await gismetio_gryzi_now()
    # Здесь можно добавить ваш код

async def job2():
    await gismetio_lipetsk_today()
    await asyncio.sleep(2)
    await gismetio_dankov_today()
    await asyncio.sleep(2)
    await gismetio_yelets_today()
    await asyncio.sleep(2)
    await gismetio_gryzi_today()
    await asyncio.sleep(2)
    await gismetio_chaplygin_today()
    # Здесь можно добавить ваш код

async def job3():
    await gismetio_lipetsk_days()
    await asyncio.sleep(1)
    await gismetio_dankov_days()
    await asyncio.sleep(1)
    await gismetio_yelets_days()
    await asyncio.sleep(1)
    await gismetio_gryzi_days()
    await asyncio.sleep(1)
    await gismetio_chaplygin_days()



@app.on_event("startup")
async def startup_event():
    # Создаем асинхронный шедулер
    scheduler = AsyncIOScheduler()


    # Добавляем задачи в шедулер
    scheduler.add_job(job1, IntervalTrigger(minutes=15))
    scheduler.add_job(job2, CronTrigger(hour=0, minute=0, second=0))
    scheduler.add_job(job3, CronTrigger(hour=0, minute=0, second=10))

    # Запускаем шедулер
    scheduler.start()





if __name__ == "__main__":
    uvicorn.run(app="main:app", port=8000, reload=True)
