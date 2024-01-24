from datetime import timedelta

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import Response

from api.dependencies import UOWDep, get_user
from models.user_role import UserRoleEnum
from models.users import Users
from schemas.users import UserSchemaRegister, UserSchemaAuth, UserSchema
from services.auth_service import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token, get_password_hash
from services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# @router.post("")
# async def add_user(
#     user: UserSchemaAdd,
#     uow: UOWDep,
# ):
#     user_id = await UsersService().add_user(uow, user)
#     return {"user_id": user_id}
#
#
# @router.get("")
# async def get_users(
#     uow: UOWDep,
# ):
#     users = await UsersService().get_users(uow)
#     return users

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
    access_token = create_access_token(
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
async def register(user_register: UserSchemaRegister, uow: UOWDep, response: Response):
    user_by_email = await UserService.get_user_by_email(uow, user_register.email)
    if user_by_email:
        raise HTTPException(status_code=409, detail="User already exists")
    # TODO: disabled True for email confirm
    user_model: Users = Users(fio=user_register.fio,
                              email=user_register.email,
                              password=get_password_hash(user_register.password),
                              disabled=False,
                              role=UserRoleEnum.user)
    user_model = await UserService.add_user(uow, user_model)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_model.id}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return UserSchema.model_validate(user_model)
