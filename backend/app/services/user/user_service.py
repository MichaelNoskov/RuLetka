from typing import Optional
import hashlib
from app.domain.models import User
from app.domain.exceptions import *
from app.api.schemas.requests.user import UserRegister, UserInfo
from app.adapters.repositories.user import AbstractUserRepository

class UserService:
    def __init__(self, user_repo: AbstractUserRepository):
        self.user_repo = user_repo
    
    async def register(self, user_data: UserRegister) -> User:
        """Регистрация нового пользователя"""
        if len(user_data.username) < 3:
            raise UsernameTooShortError("Имя пользователя слишком короткое")

        existing = await self.user_repo.get_by_username(user_data.username)
        if existing:
            raise UserAlreadyExistsError("Пользователь уже существует")

        user = User(
            username=user_data.username,
            is_male=user_data.is_male,
            birthdate=user_data.birthdate,
            country=user_data.country,
            description=user_data.description,
            hashed_password=self._hash_password(user_data.password)
        )
        return await self.user_repo.create(user)
    
    async def login(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = await self.user_repo.get_by_username(username)
        if not user or self._hash_password(password) != user.hashed_password:
            raise InvalidPasswordError("Неверный логин или пароль")
        return user
    
    async def get_profile(self, user_id: int) -> Optional[User]:
        """Получить профиль пользователя"""
        return await self.user_repo.get_by_id(user_id)
    
    async def update_profile(self, user_id: int, data: UserInfo) -> User:
        """Обновить профиль пользователя"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")

        user.username = data.username
        user.is_male = data.is_male
        user.birthdate = data.birthdate
        user.country = data.country
        user.description = data.description
        
        return await self.user_repo.update(user)
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
