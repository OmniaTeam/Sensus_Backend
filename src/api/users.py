from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Cookie, Response
from starlette import status
from starlette.responses import RedirectResponse

from api.dependencies import UOWDep, get_user
from models.user_role import UserRoleEnum
from models.users import Users
from schemas.users import UserSchemaRegister, UserSchemaAuth, UserSchema
from services.auth_service import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, create_token, \
    create_email_token, get_confirm_user, create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_DAYS
from services.email_service import send_email
from services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/token")
async def login_for_access_token(
        user_register: UserSchemaAuth,
        response: Response,
        uow: UOWDep
):
    user: Users = await authenticate_user(uow, user_register.email, user_register.password)
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

    return


@router.get("/me", response_model=UserSchema)
async def read_users_me(
        current_user: get_user
):
    return UserSchema.model_validate(current_user)


@router.post("/register", status_code=201)
async def register(user_register: UserSchemaRegister, uow: UOWDep):
    user_by_email = await UserService.get_user_by_email(uow, user_register.email)
    if user_by_email:
        if user_by_email.enabled:
            raise HTTPException(status_code=409, detail="User already exists")
        else:
            await UserService.delete_user_by_id(uow, user_by_email.id)
    user_model: Users = Users(fio=user_register.fio,
                              email=user_register.email,
                              password=get_password_hash(user_register.password),
                              enabled=False,
                              role=UserRoleEnum.user)

    user_model = await UserService.add_user(uow, user_model)
    email_token = create_email_token(
        data={"user_id": user_model.id})
    send_email(user_register.email, "http://localhost:8080/api/users/confirm/" + email_token)
    return UserSchema.model_validate(user_model)


@router.get("/refresh", status_code=200)
async def refresh(uow: UOWDep, response: Response, refresh_token: Annotated[str | None, Cookie()] = None):
    user: Users = await get_confirm_user(uow, refresh_token)
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
    user: Users = await get_confirm_user(uow, token)
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
