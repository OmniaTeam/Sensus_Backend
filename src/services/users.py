from models.users import Users
from schemas.users import UserSchemaRegister
from utils.unitofwork import IUnitOfWork


class UserService:
    @staticmethod
    async def add_user(uow: IUnitOfWork, user: Users):

        async with uow:
            user = await uow.users.add_one(user=user)
            await uow.commit()
            return user

    @staticmethod
    async def get_users(uow: IUnitOfWork):
        async with uow:
            users = await uow.users.find_all()
            return users

    @staticmethod
    async def get_user_by_id(uow: IUnitOfWork, user_id: int):
        async with uow:
            user = await uow.users.find_one(id=user_id)
            return user

    @staticmethod
    async def get_user_by_email(uow: IUnitOfWork, email: str):
        async with uow:
            user = await uow.users.find_one(email=email)
            return user
