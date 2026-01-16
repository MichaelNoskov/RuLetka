from dataclasses import dataclass
from typing import Dict, Any

from app.core.ports.services.webrtc_manager import AbstractWebRTCManager
from app.application.mappers.webrtc_mapper import WebRTCMapper


@dataclass
class HandleAnswerUseCaseImpl:
    webrtc_manager: AbstractWebRTCManager
    
    async def execute(
        self,
        room_id: str,
        client_id: str,
        sdp: str,
        sdp_type: str
    ) -> Dict[str, Any]:
        result = await self.webrtc_manager.handle_answer(
            room_id=room_id,
            client_id=client_id,
            sdp=sdp,
            sdp_type=sdp_type
        )
        
        return WebRTCMapper.to_answer_response(result)
