from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AbstractWebRTCManager(ABC):
    @abstractmethod
    async def initiate_connection(
        self,
        user_id: str,
        gender_filter: Optional[bool] = None,
        age_filter: Optional[int] = None,
        country_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def move_connection_to_room(
        self,
        temp_id: str,
        room_id: str
    ) -> str:
        pass
    
    @abstractmethod
    async def handle_answer(
        self,
        room_id: str,
        client_id: str,
        sdp: str,
        sdp_type: str
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def cleanup_connection(self, client_id: str) -> None:
        pass
    
    @abstractmethod
    async def get_room_users(self, room_id: str) -> List[str]:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass
