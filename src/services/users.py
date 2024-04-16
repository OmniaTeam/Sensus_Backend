from models.models import User
from schemas.users import UserSchemaRegister
from utils.unitofwork import IUnitOfWork


class UserService:

    @staticmethod
    async def add_user(uow: IUnitOfWork, user: User):

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

    @staticmethod
    async def update_user_by_id(uow: IUnitOfWork, id: int, data: dict):
        async with uow:
            user = await uow.users.edit_one(id, data)
            return user

    @staticmethod
    async def delete_user_by_id(uow: IUnitOfWork, id: int):
        async with uow:
            await uow.users.delete_one(id)
            await uow.commit()
