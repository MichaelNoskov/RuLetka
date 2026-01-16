from dataclasses import dataclass
from typing import Any

from app.core.exceptions import UserNotFoundError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.usecases.user import GetUserProfileUseCase
from app.application.mappers.user_mapper import UserMapper


@dataclass
class GetUserProfileUseCaseImpl(GetUserProfileUseCase):
    user_repo: AbstractUserRepository
    
    async def execute(self, user_id: int) -> dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        return UserMapper.domain_to_api_response(user)
    
    async def execute_by_username(self, username: str) -> dict[str, Any]:
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        return UserMapper.domain_to_api_response(user)
