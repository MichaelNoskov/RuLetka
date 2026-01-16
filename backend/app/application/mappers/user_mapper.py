from typing import Any

from app.core.entities.user import User
from app.core.value_objects.user_id import UserID


class UserMapper:
    
    @staticmethod
    def api_to_create_dto(api_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "username": api_data.get("username"),
            "password": api_data.get("password"),
            "is_male": api_data.get("is_male"),
            "birthdate": api_data.get("birthdate"),
            "country": api_data.get("country"),
            "description": api_data.get("description", "")
        }
    
    @staticmethod
    def api_to_update_dto(api_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "username": api_data.get("username"),
            "is_male": api_data.get("is_male"),
            "birthdate": api_data.get("birthdate"),
            "country": api_data.get("country"),
            "description": api_data.get("description", "")
        }
    
    @staticmethod
    def api_to_login_dto(api_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "username": api_data.get("username"),
            "password": api_data.get("password")
        }
    
    @staticmethod
    def domain_to_api_response(user: User) -> dict[str, Any]:
        return {
            "id": user.id.value,
            "username": user.username,
            "is_male": user.is_male,
            "birthdate": user.birthdate,
            "country": user.country,
            "description": user.description,
            "photo_url": user.photo_url
        }
    
    @staticmethod
    def dict_to_domain(data: dict[str, Any]) -> User:
        return User(
            id=UserID(data.get("id")),
            username=data["username"],
            is_male=data["is_male"],
            birthdate=data["birthdate"],
            country=data["country"],
            description=data.get("description", ""),
            hashed_password=data["hashed_password"],
            photo_url=data.get("photo_url", "default_avatar.jpg")
        )
