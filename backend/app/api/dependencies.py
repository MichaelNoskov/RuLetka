from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.adapters.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.adapters.repositories.minio_file_storage import MinIOFileStorage
from app.infrastructure.adapters.repositories.bcrypt_hasher import BCryptPasswordHasher
from app.infrastructure.adapters.repositories.jwt_provider import JWTTokenProvider
from app.infrastructure.external.dicebear_avatar_provider import DiceBearBotttsProvider
from app.infrastructure.database.connection import get_db
from app.infrastructure.config.settings import settings
from app.services.user.user_service import UserService


async def get_user_repo(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserRepository(session)

async def get_password_hasher():
    return BCryptPasswordHasher()

async def get_token_provider():
    return JWTTokenProvider(settings.JWT_SECRET_KEY)

async def get_file_storage(bucket: str):
    return MinIOFileStorage(bucket)

async def get_avatar_storage():
    return await get_file_storage(settings.MINIO_AVATAR_BUCKET)

async def get_avatar_provider():
    return DiceBearBotttsProvider()

async def get_user_service(
    user_repo=Depends(get_user_repo),
    password_hasher=Depends(get_password_hasher),
    avatar_storage=Depends(get_avatar_storage),
    avatar_provider=Depends(get_avatar_provider)
):
    yield UserService(user_repo, password_hasher, avatar_storage, avatar_provider)
