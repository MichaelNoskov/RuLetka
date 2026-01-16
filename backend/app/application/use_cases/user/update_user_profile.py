from dataclasses import dataclass
from typing import Any
from datetime import date

from app.core.exceptions import UserNotFoundError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.usecases.user import UpdateUserProfileUseCase
from app.application.mappers.user_mapper import UserMapper


@dataclass
class UpdateUserProfileUseCaseImpl(UpdateUserProfileUseCase):
    user_repo: AbstractUserRepository
    
    async def execute(
        self,
        user_id: int,
        username: str,
        is_male: bool,
        birthdate: date,
        country: str,
        description: str = ""
    ) -> dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        user.username = username
        user.is_male = is_male
        user.birthdate = birthdate
        user.country = country
        user.description = description
        
        updated_user = await self.user_repo.update(user)

        return UserMapper.domain_to_api_response(updated_user)
