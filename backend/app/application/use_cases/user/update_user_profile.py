from dataclasses import dataclass

from app.core.entities.user import User
from app.core.exceptions import UserNotFoundError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.application.dto.user import UserUpdateDTO


@dataclass
class UpdateUserProfileUseCase:
    user_repo: AbstractUserRepository
    
    async def execute(self, user_id: int, dto: UserUpdateDTO) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        user.update_profile(
            username=dto.username,
            is_male=dto.is_male,
            birthdate=dto.birthdate,
            country=dto.country,
            description=dto.description
        )
        
        return await self.user_repo.update(user)
