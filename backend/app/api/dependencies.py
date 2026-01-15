from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.adapters.repositories.user import SQLAlchemyUserRepository
from app.services.user.user_service import UserService
from app.infrastructure.database.connection import get_db

async def get_user_repo(session: AsyncSession = Depends(get_db)):
    """Зависимость для UserRepository"""
    yield SQLAlchemyUserRepository(session)

async def get_user_service(repo=Depends(get_user_repo)):
    """Зависимость для UserService"""
    yield UserService(repo)
