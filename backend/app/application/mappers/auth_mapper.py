from typing import Any
from app.core.entities.user import User


class AuthMapper:
    
    @staticmethod
    def domain_to_login_response(user: User, token: str) -> dict[str, Any]:
        return {
            "id": user.id.value,
            "username": user.username,
            "is_male": user.is_male,
            "birthdate": user.birthdate,
            "country": user.country,
            "description": user.description,
            "photo_url": user.photo_url,
            "token": token
        }
