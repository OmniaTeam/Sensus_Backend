from fastapi import APIRouter

router = APIRouter(
    prefix="/healthcheck",
    tags=["Healthcheck"],
)


@router.get("", status_code=200)
async def healthcheck():
    return "Ok"
