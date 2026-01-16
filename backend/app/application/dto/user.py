from dataclasses import dataclass
from datetime import date


@dataclass
class UserCreateDTO:
    username: str
    password: str
    is_male: bool
    birthdate: date
    country: str
    description: str

@dataclass
class UserUpdateDTO:
    username: str
    is_male: bool
    birthdate: date
    country: str
    description: str

@dataclass
class AvatarUploadDTO:
    user_id: int
    image_bytes: bytes
    size: tuple = (256, 256)
    quality: int = 85
