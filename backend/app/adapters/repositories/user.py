from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import User

class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]: ...

class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        # TODO: реализация с SQLAlchemy
        return user
    
    async def get_by_username(self, username: str) -> Optional[User]:
        # TODO: Реализация поиска
        model_username = "Michael"
        if username != model_username:
            return
        from app.services.user.user_service import UserService
        return User(model_username, True, "2006-02-14", "Russian", "", UserService._hash_password(None, "12345678"))
