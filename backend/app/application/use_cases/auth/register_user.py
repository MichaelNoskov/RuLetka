from dataclasses import dataclass

from app.core.entities.user import User
from app.core.exceptions import UsernameTooShortError, UserAlreadyExistsError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.password_hasher import AbstractPasswordHasher
from app.core.ports.services.avatar_provider import AbstractAvatarProvider
from app.core.ports.services.file_storage import AbstractFileStorage
from app.core.ports.services.image_processor import AbstractImageProcessor
from app.application.dto.user import UserCreateDTO


@dataclass
class RegisterUserUseCase:
    user_repo: AbstractUserRepository
    password_hasher: AbstractPasswordHasher
    avatar_provider: AbstractAvatarProvider
    avatar_storage: AbstractFileStorage
    image_processor: AbstractImageProcessor
    default_avatar_filename: str = "default_avatar.jpg"
    
    async def execute(self, dto: UserCreateDTO) -> User:
        if len(dto.username) < 3:
            raise UsernameTooShortError("Имя пользователя слишком короткое")

        existing = await self.user_repo.get_by_username(dto.username)
        if existing:
            raise UserAlreadyExistsError("Пользователь уже существует")

        user = User(
            username=dto.username,
            is_male=dto.is_male,
            birthdate=dto.birthdate,
            country=dto.country,
            description=dto.description,
            hashed_password=self.password_hasher.hash(dto.password),
            photo_url=self.default_avatar_filename
        )

        created_user = await self.user_repo.create(user)

        image_bytes = await self.avatar_provider.get_random()
        if image_bytes:
            processed = self.image_processor.process_avatar(
                image_bytes, size=(256, 256), quality=85
            )
            file_url = await self.avatar_storage.save_file(
                f"avatar_{created_user.user_id}", processed
            )
            if file_url:
                created_user.photo_url = file_url
                await self.user_repo.update(created_user)
        
        return created_user
