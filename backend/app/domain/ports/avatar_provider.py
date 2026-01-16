from abc import ABC, abstractmethod
from typing import Optional


class AbstractAvatarProvider(ABC):
    
    @abstractmethod
    async def get_random(self) -> Optional[bytes]:
        pass
    
    @abstractmethod
    async def get_by_name(self, username: str) -> Optional[bytes]:
        pass
