from abc import ABC, abstractmethod
from typing import Optional


class AbstractFileStorage(ABC):
    @abstractmethod
    async def save_file(self, filename: str, content: bytes, bucket: str) -> str:
        pass
    
    @abstractmethod
    async def get_file(self, filename: str, bucket: str) -> Optional[bytes]:
        pass
    
    @abstractmethod
    async def delete_file(self, filename: str, bucket: str) -> bool:
        pass
