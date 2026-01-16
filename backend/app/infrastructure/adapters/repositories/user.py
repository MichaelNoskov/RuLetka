from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.ports.user_repository import AbstractUserRepository
from app.domain.models.user import User
from app.domain.exceptions import UserNotFoundError
from app.infrastructure.database.models.user import User as UserModel


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, db_user: UserModel) -> User:
        return User(
            id=db_user.id,
            username=db_user.username,
            is_male=db_user.is_male,
            birthdate=db_user.birthdate,
            country=db_user.country,
            description=db_user.description or "",
            hashed_password=db_user.password,
            photo_url=db_user.photo_url
        )
    
    def _to_db(self, domain_user: User) -> UserModel:
        return UserModel(
            username=domain_user.username,
            is_male=domain_user.is_male,
            birthdate=domain_user.birthdate,
            country=domain_user.country,
            description=domain_user.description,
            password=domain_user.hashed_password,
            photo_url=domain_user.photo_url
        )
    
    async def create(self, user: User) -> User:
        db_user = self._to_db(user)

        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)

        return self._to_domain(db_user)

    async def update(self, user: User) -> User:
        if not user.id:
            raise UserNotFoundError("Пользователь ещё не сохранён в бд")

        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise UserNotFoundError("Пользователь не найден")

        db_user.username = user.username
        db_user.is_male = user.is_male
        db_user.birthdate = user.birthdate
        db_user.country = user.country
        db_user.description = user.description
        db_user.password = user.hashed_password
        db_user.photo_url = user.photo_url
        
        await self.session.commit()
        await self.session.refresh(db_user)
        
        return self._to_domain(db_user)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return self._to_domain(db_user)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return self._to_domain(db_user)

    async def delete(self, user_id: int) -> bool:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return False
        
        await self.session.delete(db_user)
        await self.session.commit()
        
        return True
