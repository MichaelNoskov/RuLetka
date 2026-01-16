from dataclasses import dataclass
from typing import Tuple

from app.core.entities.user import User
from app.core.exceptions import InvalidPasswordError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.password_hasher import AbstractPasswordHasher
from app.core.ports.services.token_provider import AbstractTokenProvider
from app.application.dto.auth import LoginDTO


@dataclass
class LoginUserUseCase:
    user_repo: AbstractUserRepository
    password_hasher: AbstractPasswordHasher
    token_provider: AbstractTokenProvider
    
    async def execute(self, dto: LoginDTO) -> Tuple[User, str]:
        user = await self.user_repo.get_by_username(dto.username)
        if not user or not self.password_hasher.verify(dto.password, user.hashed_password):
            raise InvalidPasswordError("Неправильный логин или пароль")
        
        token = self.token_provider.create(str(user.user_id))
        return user, token
