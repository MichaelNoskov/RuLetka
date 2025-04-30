from pydantic import BaseModel, Field


class SearchRoom(BaseModel):
    is_male: bool | None = Field(default=None, description="Пол пользователя (True - мужской, False - женский)")
    age: int | None = Field(default=None)
    country: str | None = Field(default=None, max_length=50)

