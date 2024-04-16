from models.models import User
from utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User
