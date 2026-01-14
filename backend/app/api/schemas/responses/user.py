from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from app.domain.models import User
from app.api.schemas.requests.user import UserInfo

class UserResponse(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., max_length=50)
    is_male: bool = Field(..., description="Пол пользователя (True - мужской, False - женский)")
    birthdate: date
    country: str = Field(..., max_length=50)
    description: str = Field(..., max_length=500)

    class Config:
        from_attributes = True

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            username=user.username,
            is_male=user.is_male,
            birthdate=user.birthdate,
            country=user.country,
            description=user.description
        )
