from dataclasses import dataclass

from app.core.entities.user import User
from app.core.exceptions import UserNotFoundError
from app.core.ports.repositories.user_repository import AbstractUserRepository


@dataclass
class GetUserProfileUseCase:
    user_repo: AbstractUserRepository
    
    async def execute(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")
        return user
