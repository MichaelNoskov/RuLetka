from typing import Optional
import io
from PIL import Image

from app.domain.models.user import User
from app.domain.exceptions import *
from app.api.schemas.requests.user import UserRegister, UserInfo
from app.domain.ports.user_repository import AbstractUserRepository
from app.domain.ports.password_hasher import AbstractPasswordHasher
from app.domain.ports.file_storage import AbstractFileStorage
from app.domain.ports.avatar_provider import AbstractAvatarProvider
from app.domain.ports.image_processor import AbstractImageProcessor
from app.domain.exceptions import UserNotFoundError


class UserService:
    def __init__(
        self,
        user_repo: AbstractUserRepository,
        password_hasher: AbstractPasswordHasher,
        avatar_storage: AbstractFileStorage,
        avatar_provider: AbstractAvatarProvider,
        image_processor: AbstractImageProcessor,
        default_avatar_filename: str = "default_avatar.jpg"
    ):
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.avatar_storage = avatar_storage
        self.avatar_provider = avatar_provider
        self.image_processor = image_processor
        self.default_avatar_filename = default_avatar_filename
    
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
            hashed_password=self.password_hasher.hash(user_data.password),
            photo_url=self.default_avatar_filename
        )

        created_user = await self.user_repo.create(user)

        image_bytes = await self.avatar_provider.get_random()
        if image_bytes:
            await self.upload_avatar(created_user.id, image_bytes)
        
        return created_user
    
    async def login(self, username: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_by_username(username)
        if not user or not self.password_hasher.verify(password, user.hashed_password):
            raise InvalidPasswordError("Неправильный логин или пароль")
        return user

    async def get_profile(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.user_repo.get_by_username(username)
    
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
    
    async def upload_avatar(self, user_id: int, image_bytes: bytes, 
                                   size: tuple = (256, 256)) -> str:

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")
    
        processed_bytes = self.image_processor.process_avatar(
            image_bytes, 
            size=size,
            quality=85
        )
        
        file_url = await self.avatar_storage.save_file(f"avatar_{user_id}", processed_bytes)
        if not file_url:
            raise NotFound("Файл не найден")

        user.photo_url = file_url
        await self.user_repo.update(user)

        return file_url
    
    async def load_avatar(self, user_id: int) -> bytes:

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")
        
        return await self.avatar_storage.get_file(user.photo_url)
