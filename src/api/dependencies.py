from typing import Annotated

from fastapi import Depends

from models.users import Users
from services.auth_service import get_current_active_user
from services.users import UserService
from utils.unitofwork import IUnitOfWork, UnitOfWork

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]

user_service = Annotated[UserService, Depends(UserService)]
get_user = Annotated[Users, Depends(get_current_active_user)]
