from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class GetUserProfileUseCase(ABC):
    @abstractmethod
    async def execute(self, user_id: int) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def execute_by_username(self, username: str) -> dict[str, Any]:
        pass


class UpdateUserProfileUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        user_id: int,
        username: str,
        is_male: bool,
        birthdate: date,
        country: str,
        description: str = ""
    ) -> dict[str, Any]:
        pass


class UploadUserAvatarUseCase(ABC):
    @abstractmethod
    async def execute(self, user_id: int, image_bytes: bytes) -> dict[str, Any]:
        pass


class LoadUserAvatarUseCase(ABC):
    @abstractmethod
    async def execute(self, user_id: int) -> bytes:
        pass
