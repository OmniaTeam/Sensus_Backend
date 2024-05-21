from api.healthcheck import router as healthcheck_router
from api.openApi import router as open_router
from api.users import router as user_router
all_routers = [healthcheck_router, user_router, open_router]
