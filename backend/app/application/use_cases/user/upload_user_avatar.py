from dataclasses import dataclass

from app.core.exceptions import UserNotFoundError
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.file_storage import AbstractFileStorage
from app.core.ports.services.image_processor import AbstractImageProcessor
from app.application.dto.user import AvatarUploadDTO


@dataclass
class UploadUserAvatarUseCase:
    user_repo: AbstractUserRepository
    avatar_storage: AbstractFileStorage
    image_processor: AbstractImageProcessor
    
    async def execute(self, dto: AvatarUploadDTO) -> str:
        user = await self.user_repo.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")
    
        processed_bytes = self.image_processor.process_avatar(
            dto.image_bytes, 
            size=dto.size,
            quality=dto.quality
        )
        
        file_url = await self.avatar_storage.save_file(
            f"avatar_{dto.user_id}", 
            processed_bytes
        )
        
        user.photo_url = file_url
        await self.user_repo.update(user)

        return file_url
