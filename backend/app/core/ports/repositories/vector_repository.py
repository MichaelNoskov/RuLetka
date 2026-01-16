from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import numpy as np


class AbstractVectorRepository(ABC):
    @abstractmethod
    async def save_user_vector(
        self, 
        user_id: str, 
        vector: np.ndarray,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        country: Optional[str] = None
    ) -> None:
        pass
    
    @abstractmethod
    async def search_rooms(
        self,
        query_vector: np.ndarray,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        country: Optional[str] = None
    ) -> List[str]:
        pass
    
    @abstractmethod
    async def delete_room(self, room_id: str) -> None:
        pass
    
    @abstractmethod
    async def get_user_vector(self, user_id: str) -> Optional[np.ndarray]:
        pass
