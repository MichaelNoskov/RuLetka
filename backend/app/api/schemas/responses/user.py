from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class UserResponse(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., max_length=50)
    is_male: bool = Field(..., description="Пол пользователя (True - мужской, False - женский)")
    birthdate: date
    country: str = Field(..., max_length=50)
    description: str = Field(..., max_length=500)

    class Config:
        from_attributes = True
