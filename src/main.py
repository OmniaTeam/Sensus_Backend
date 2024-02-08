import uvicorn
from fastapi import FastAPI, APIRouter

from api.routers import all_routers

app = FastAPI(
    title="Sensus Weather",
    debug=True,
    docs_url="/api/docs"
)
main_router = APIRouter(prefix="/api")

for router in all_routers:
    main_router.include_router(router)

app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", port=8080, reload=True)
