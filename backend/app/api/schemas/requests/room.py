from pydantic import BaseModel, Field
from typing import Optional


class SearchRoomRequest(BaseModel):
    is_male: Optional[bool] = Field(None, description="Фильтр по полу")
    age: Optional[int] = Field(None, ge=18, le=100, description="Фильтр по возрасту")
    country: Optional[str] = Field(None, description="Фильтр по стране")

class AnswerRequest(BaseModel):
    sdp: str = Field(..., description="SDP ответа")
    type: str = Field(..., description="Тип SDP")
    id: str = Field(..., description="ID клиента")
    room_id: str = Field(..., description="ID комнаты")
