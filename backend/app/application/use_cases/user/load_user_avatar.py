from dataclasses import dataclass

from app.core.exceptions import UserNotFoundError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.file_storage import AbstractFileStorage
from app.core.exceptions import NotFound


@dataclass
class LoadUserAvatarUseCase:
    user_repo: AbstractUserRepository
    avatar_storage: AbstractFileStorage
    
    async def execute(self, user_id: int) -> bytes:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")
        
        image_bytes = await self.avatar_storage.get_file(user.photo_url)
        if not image_bytes:
            raise NotFound("Аватар не найден")
        
        return image_bytes
