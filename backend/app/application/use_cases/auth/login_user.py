from dataclasses import dataclass
from typing import Any

from app.core.exceptions import InvalidPasswordError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.password_hasher import AbstractPasswordHasher
from app.core.ports.services.token_provider import AbstractTokenProvider
from app.core.ports.usecases.auth import LoginUserUseCase
from app.application.mappers.auth_mapper import AuthMapper


@dataclass
class LoginUserUseCaseImpl(LoginUserUseCase):
    user_repo: AbstractUserRepository
    password_hasher: AbstractPasswordHasher
    token_provider: AbstractTokenProvider
    
    async def execute(
        self,
        username: str,
        password: str
    ) -> dict[str, Any]:
        
        user = await self.user_repo.get_by_username(username)
        if not user or not self.password_hasher.verify(password, user.hashed_password):
            raise InvalidPasswordError("Неправильный логин или пароль")
        
        token = self.token_provider.create(str(user.id.value))
        
        return AuthMapper.domain_to_login_response(user, token)
