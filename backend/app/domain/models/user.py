from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class User:
    username: str
    is_male: bool
    birthdate: date
    country: str
    description: str
    hashed_password: str
    id: Optional[int] = None
