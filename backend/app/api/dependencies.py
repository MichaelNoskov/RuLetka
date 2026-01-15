from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.adapters.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.adapters.repositories.bcrypt_hasher import BCryptPasswordHasher
from app.infrastructure.adapters.repositories.jwt_provider import JWTTokenProvider
from app.services.user.user_service import UserService
from app.infrastructure.database.connection import get_db
from app.infrastructure.config.settings import settings

async def get_user_repo(session: AsyncSession = Depends(get_db)):
    """Зависимость для UserRepository"""
    yield SQLAlchemyUserRepository(session)

async def get_password_hasher():
    return BCryptPasswordHasher()

async def get_token_provider():
    return JWTTokenProvider(settings.JWT_SECRET_KEY)

async def get_user_service(user_repo=Depends(get_user_repo), password_hasher=Depends(get_password_hasher)):
    """Зависимость для UserService"""
    yield UserService(user_repo, password_hasher)

