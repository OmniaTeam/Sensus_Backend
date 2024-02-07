from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Cookie
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from config import config_project
from models.users import Users
from services.users import UserService
from utils.unitofwork import IUnitOfWork, UnitOfWork

SECRET_KEY = config_project.token.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(config_project.token.access_token_expire_minute)
REFRESH_TOKEN_EXPIRE_DAYS = int(config_project.token.refresh_token_expire_days)
EMAIL_TOKEN_EXPIRE_MINUTES = int(config_project.token.email_token_expire_minute)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(uow: Annotated[IUnitOfWork, Depends(UnitOfWork)], email: str, password: str):
    user = await UserService.get_user_by_email(uow, email)
    if user and verify_password(password, user.password):
        return user
    return False


def create_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict):
    return create_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict):
    return create_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def create_email_token(data: dict):
    return create_token(data, timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES))


async def get_current_user(uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
                           access_token: Annotated[str | None, Cookie()] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError as er:
        print(er)
        raise credentials_exception
    user = await UserService.get_user_by_id(uow, user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_confirm_user(uow, token):
    return await get_current_user(uow, token)


async def get_current_active_user(
        current_user: Annotated[Users, Depends(get_current_user)]
):
    if not current_user.enabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
