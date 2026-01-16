from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class InitiateConnectionUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        user_id: str,
        gender_filter: Optional[bool] = None,
        age_filter: Optional[int] = None,
        country_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        pass

class HandleAnswerUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        room_id: str,
        client_id: str,
        sdp: str,
        sdp_type: str
    ) -> Dict[str, Any]:
        pass

class WebRTCOutputPort(ABC):
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
    async def handle_answer(
        self,
        room_id: str,
        client_id: str,
        sdp: str,
        sdp_type: str
    ) -> Dict[str, Any]:
        pass
