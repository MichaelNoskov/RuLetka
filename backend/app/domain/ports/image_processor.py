from abc import ABC, abstractmethod
from typing import Tuple


class AbstractImageProcessor(ABC):
    
    @abstractmethod
    def process_avatar(
        self, 
        image_bytes: bytes, 
        size: Tuple[int, int] = (256, 256),
        quality: int = 85
    ) -> bytes:
        pass
