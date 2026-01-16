from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.core.value_objects.user_id import UserID


@dataclass
class User:
    username: str
    is_male: bool
    birthdate: date
    country: str
    description: str
    hashed_password: str
    photo_url: str
    id: UserID = UserID()
    
    @property
    def user_id(self) -> Optional[int]:
        return self.id.value
    
    def update_profile(self, username: str, is_male: bool, 
                      birthdate: date, country: str, description: str) -> None:
        self.username = username
        self.is_male = is_male
        self.birthdate = birthdate
        self.country = country
        self.description = description
