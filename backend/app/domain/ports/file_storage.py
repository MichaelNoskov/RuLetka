from abc import ABC, abstractmethod
from typing import Optional


class AbstractFileStorage(ABC):
    @property
    @abstractmethod
    def bucket(self) -> str:
        pass
    
    @abstractmethod
    async def save_file(self, filename: str, image_bytes: bytes) -> str:
        pass
    
    @abstractmethod
    async def get_file(self, filename: str) -> Optional[bytes]:
        pass
