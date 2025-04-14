from pydantic import BaseModel, Field
from pydantic.types import PastDate
from uuid import UUID


class Tocken(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class UserLogin(BaseModel):
    id: UUID = None
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

class UserInfo(BaseModel):
    username: str = Field(..., max_length=50)
    is_male: bool = Field(..., description="Пол пользователя (True - мужской, False - женский)")
    birthdate: PastDate
    country: str = Field(..., max_length=50)
    description: str = Field("", max_length=500)

class UserRegister(UserInfo):
    password: str = Field(..., min_length=8, max_length=128)
