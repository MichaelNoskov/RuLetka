from pydantic import BaseModel
from uuid import UUID

class HobbySchema(BaseModel):
    id: UUID
    title: str

    class Config:
        orm_mode = True

class HobbyCreate(BaseModel):
    title: str

class HobbyList(BaseModel):
    hobbies: list[HobbySchema]
