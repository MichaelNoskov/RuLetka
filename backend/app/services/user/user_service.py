from typing import Optional

from app.domain.models.user import User
from app.domain.exceptions import *
from app.api.schemas.requests.user import UserRegister, UserInfo
from app.domain.ports.user_repository import AbstractUserRepository
from app.domain.ports.password_hasher import AbstractPasswordHasher

class UserService:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        password_hasher: AbstractPasswordHasher
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
    
    async def register(self, user_data: UserRegister) -> User:
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
            hashed_password=self.password_hasher.hash(user_data.password)
        )
        return await self.user_repo.create(user)
    
    async def login(self, username: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_by_username(username)
        print(user, flush=True)
        if not user or not self.password_hasher.verify(password, user.hashed_password):
            raise InvalidPasswordError("Неправильный логин или пароль")
        return user

    async def get_profile(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
    
    async def update_profile(self, user_id: int, data: UserInfo) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        user.username = data.username
        user.is_male = data.is_male
        user.birthdate = data.birthdate
        user.country = data.country
        user.description = data.description
        
        return await self.user_repo.update(user)
