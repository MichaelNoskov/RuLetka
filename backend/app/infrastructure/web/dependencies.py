from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.application.use_cases.user.get_user_profile import GetUserProfileUseCase
from app.application.use_cases.user.update_user_profile import UpdateUserProfileUseCase
from app.application.use_cases.user.upload_user_avatar import UploadUserAvatarUseCase
from app.application.use_cases.user.load_user_avatar import LoadUserAvatarUseCase

from app.infrastructure.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.adapters.services.bcrypt_hasher import BCryptPasswordHasher
from app.infrastructure.adapters.services.jwt_token_provider import JWTTokenProvider
from app.infrastructure.adapters.services.minio_file_storage import MinIOFileStorage
from app.infrastructure.adapters.services.pillow_image_processor import PillowImageProcessor
from app.infrastructure.external.dicebear_avatar_provider import DiceBearBotttsProvider

from app.infrastructure.database.connection import get_db
from app.infrastructure.config.settings import settings


async def get_user_repo(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserRepository(session)

async def get_password_hasher() -> BCryptPasswordHasher:
    return BCryptPasswordHasher()

async def get_token_provider() -> JWTTokenProvider:
    return JWTTokenProvider(settings.JWT_SECRET_KEY)

async def get_avatar_storage() -> MinIOFileStorage:
    storage = MinIOFileStorage(settings.MINIO_AVATAR_BUCKET)
    return storage

async def get_avatar_provider() -> DiceBearBotttsProvider:
    return DiceBearBotttsProvider()

async def get_image_processor() -> PillowImageProcessor:
    return PillowImageProcessor()

async def get_register_use_case(
    user_repo=Depends(get_user_repo),
    password_hasher=Depends(get_password_hasher),
    avatar_storage=Depends(get_avatar_storage),
    avatar_provider=Depends(get_avatar_provider),
    image_processor=Depends(get_image_processor),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        avatar_storage=avatar_storage,
        avatar_provider=avatar_provider,
        image_processor=image_processor
    )

async def get_login_use_case(
    user_repo=Depends(get_user_repo),
    password_hasher=Depends(get_password_hasher),
    token_provider=Depends(get_token_provider),
) -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repo=user_repo,
        password_hasher=password_hasher,
        token_provider=token_provider
    )

async def get_user_profile_use_case(
    user_repo=Depends(get_user_repo),
) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(user_repo=user_repo)

async def get_update_profile_use_case(
    user_repo=Depends(get_user_repo),
) -> UpdateUserProfileUseCase:
    return UpdateUserProfileUseCase(user_repo=user_repo)

async def get_upload_avatar_use_case(
    user_repo=Depends(get_user_repo),
    avatar_storage=Depends(get_avatar_storage),
    image_processor=Depends(get_image_processor),
) -> UploadUserAvatarUseCase:
    return UploadUserAvatarUseCase(
        user_repo=user_repo,
        avatar_storage=avatar_storage,
        image_processor=image_processor
    )

async def get_load_avatar_use_case(
    user_repo=Depends(get_user_repo),
    avatar_storage=Depends(get_avatar_storage),
) -> LoadUserAvatarUseCase:
    return LoadUserAvatarUseCase(
        user_repo=user_repo,
        avatar_storage=avatar_storage
    )
