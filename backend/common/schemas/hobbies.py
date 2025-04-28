from pydantic import BaseModel
from uuid import UUID

class HobbySchema(BaseModel):
    id: UUID
    title: str
    image: str

    class Config:
        orm_mode = True

class HobbyCreate(BaseModel):
    title: str
    image: str = None


class HobbyList(BaseModel):
    hobbies: list[HobbySchema]
