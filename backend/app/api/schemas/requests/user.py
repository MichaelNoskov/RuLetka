from pydantic import BaseModel, Field
from pydantic.types import PastDate

class UserLogin(BaseModel):
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
