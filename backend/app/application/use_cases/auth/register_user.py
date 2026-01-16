from dataclasses import dataclass
from typing import Any
from datetime import date

from app.core.exceptions import UsernameTooShortError, UserAlreadyExistsError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.password_hasher import AbstractPasswordHasher
from app.core.ports.services.avatar_provider import AbstractAvatarProvider
from app.core.ports.services.file_storage import AbstractFileStorage
from app.core.ports.services.image_processor import AbstractImageProcessor
from app.core.ports.usecases.auth import RegisterUserUseCase
from app.application.mappers.user_mapper import UserMapper
from app.core.entities.user import User
from app.core.value_objects.user_id import UserID


@dataclass
class RegisterUserUseCaseImpl(RegisterUserUseCase):
    user_repo: AbstractUserRepository
    password_hasher: AbstractPasswordHasher
    avatar_provider: AbstractAvatarProvider
    avatar_storage: AbstractFileStorage
    image_processor: AbstractImageProcessor
    default_avatar_filename: str = "default_avatar.jpg"
    
    async def execute(
        self,
        username: str,
        password: str,
        is_male: bool,
        birthdate: date,
        country: str,
        description: str = ""
    ) -> dict[str, Any]:

        if len(username) < 3:
            raise UsernameTooShortError("Имя пользователя слишком короткое")

        existing = await self.user_repo.get_by_username(username)
        if existing:
            raise UserAlreadyExistsError("Пользователь уже существует")
        
        user = User(
            id=UserID(),
            username=username,
            is_male=is_male,
            birthdate=birthdate,
            country=country,
            description=description,
            hashed_password=self.password_hasher.hash(password),
            photo_url=self.default_avatar_filename
        )

        created_user = await self.user_repo.create(user)

        image_bytes = await self.avatar_provider.get_random()
        if image_bytes:
            processed = self.image_processor.process_avatar(
                image_bytes, size=(256, 256), quality=85
            )
            file_url = await self.avatar_storage.save_file(
                f"avatar_{created_user.id.value}", 
                processed
            )
            if file_url:
                created_user.photo_url = file_url
                await self.user_repo.update(created_user)

        return UserMapper.domain_to_api_response(created_user)
