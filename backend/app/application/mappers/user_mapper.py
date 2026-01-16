from app.core.entities.user import User
from app.application.dto.user import UserCreateDTO


class UserMapper:
    @staticmethod
    def to_domain_from_create(dto: UserCreateDTO, hashed_password: str) -> User:
        return User(
            username=dto.username,
            is_male=dto.is_male,
            birthdate=dto.birthdate,
            country=dto.country,
            description=dto.description,
            hashed_password=hashed_password,
            photo_url="default_avatar.jpg"
        )
    
    @staticmethod
    def to_response(domain_user: User) -> dict:
        return {
            "id": domain_user.user_id,
            "username": domain_user.username,
            "is_male": domain_user.is_male,
            "birthdate": domain_user.birthdate,
            "country": domain_user.country,
            "description": domain_user.description,
            "photo_url": domain_user.photo_url
        }
