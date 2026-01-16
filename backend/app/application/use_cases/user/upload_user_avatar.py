from dataclasses import dataclass
from typing import Any

from app.core.exceptions import UserNotFoundError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.file_storage import AbstractFileStorage
from app.core.ports.services.image_processor import AbstractImageProcessor
from app.core.ports.usecases.user import UploadUserAvatarUseCase


@dataclass
class UploadUserAvatarUseCaseImpl(UploadUserAvatarUseCase):
    user_repo: AbstractUserRepository
    avatar_storage: AbstractFileStorage
    image_processor: AbstractImageProcessor
    
    async def execute(self, user_id: int, image_bytes: bytes) -> dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")
    
        processed_bytes = self.image_processor.process_avatar(
            image_bytes, 
            size=(256, 256),
            quality=85
        )
        
        file_url = await self.avatar_storage.save_file(
            f"avatar_{user_id}", 
            processed_bytes
        )
        
        user.photo_url = file_url
        await self.user_repo.update(user)

        return {"avatar_url": file_url}
