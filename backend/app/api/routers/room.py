from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Any

from app.api.schemas.requests.room import SearchRoomRequest, AnswerRequest
from app.core.ports.usecases.webrtc import WebRTCOutputPort
from app.infrastructure.web.dependencies import get_webrtc_output_port
from app.infrastructure.web.middleware.security import get_current_user_id

router = APIRouter()


@router.post('/initiate_connection')
async def initiate_connection(
    params: SearchRoomRequest,
    user_id: str = Depends(get_current_user_id),
    webrtc_port: WebRTCOutputPort = Depends(get_webrtc_output_port)
) -> dict[str, Any]:
    """
    Инициировать соединение.
    Внутри этого эндпоинта происходит:
    1. Генерация/получение вектора пользователя
    2. Поиск подходящей комнаты
    3. Сохранение пользователя для поиска (если комната не найдена)
    4. Инициализация WebRTC соединения
    """
    result = await webrtc_port.initiate_connection(
        user_id=user_id,
        gender_filter=params.is_male,
        age_filter=params.age,
        country_filter=params.country
    )
    
    return JSONResponse(content=result)

@router.post('/answer')
async def answer(
    request: AnswerRequest,
    webrtc_port: WebRTCOutputPort = Depends(get_webrtc_output_port)
) -> dict[str, Any]:
    """
    Обработать WebRTC answer.
    Внутри:
    1. Установка remote description
    2. Рассылка списка пользователей в комнате
    """
    result = await webrtc_port.handle_answer(
        room_id=request.room_id,
        client_id=request.id,
        sdp=request.sdp,
        sdp_type=request.type
    )
    
    return JSONResponse(content=result)
