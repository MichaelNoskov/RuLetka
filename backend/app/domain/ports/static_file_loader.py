from abc import ABC, abstractmethod
from typing import Optional


class AbstractStaticFileLoader(ABC):
    
    @abstractmethod
    async def load_default_avatar(self) -> Optional[bytes]:
        pass
