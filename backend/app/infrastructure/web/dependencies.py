from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast, Any, Optional

from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.vectorizer import AbstractVectorizer
from app.core.ports.repositories.vector_repository import AbstractVectorRepository
from app.core.ports.services.password_hasher import AbstractPasswordHasher
from app.core.ports.services.token_provider import AbstractTokenProvider
from app.core.ports.services.file_storage import AbstractFileStorage
from app.core.ports.services.image_processor import AbstractImageProcessor
from app.core.ports.services.avatar_provider import AbstractAvatarProvider
from app.core.ports.services.webrtc_manager import AbstractWebRTCManager

from app.core.ports.usecases.auth import LoginUserUseCase, RegisterUserUseCase
from app.core.ports.usecases.user import (
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
    UploadUserAvatarUseCase,
    LoadUserAvatarUseCase
)

from app.core.ports.usecases.webrtc import (
    InitiateConnectionUseCase,
    HandleAnswerUseCase,
    WebRTCOutputPort
)

from app.application.use_cases.auth.register_user import RegisterUserUseCaseImpl
from app.application.use_cases.auth.login_user import LoginUserUseCaseImpl
from app.application.use_cases.user.get_user_profile import GetUserProfileUseCaseImpl
from app.application.use_cases.user.update_user_profile import UpdateUserProfileUseCaseImpl
from app.application.use_cases.user.upload_user_avatar import UploadUserAvatarUseCaseImpl
from app.application.use_cases.user.load_user_avatar import LoadUserAvatarUseCaseImpl
from app.application.use_cases.room.initiate_connection import InitiateConnectionUseCaseImpl
from app.application.use_cases.room.handle_answer import HandleAnswerUseCaseImpl

from app.infrastructure.adapters.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.infrastructure.adapters.repositories.clickhouse_vector_repository import ClickHouseVectorRepository
from app.infrastructure.adapters.services.bcrypt_hasher import BCryptPasswordHasher
from app.infrastructure.adapters.services.jwt_token_provider import JWTTokenProvider
from app.infrastructure.adapters.services.minio_file_storage import MinIOFileStorage
from app.infrastructure.adapters.services.pillow_image_processor import PillowImageProcessor
from app.infrastructure.adapters.services.webrtc_manager_impl import WebRTCManagerImpl
from app.infrastructure.external.dicebear_avatar_provider import DiceBearBotttsProvider
from app.infrastructure.storage.clickhouse_client import ClickHouseAsyncClient

from app.infrastructure.database.connection import get_db
from app.infrastructure.config.settings import settings


async def get_user_repo(session: AsyncSession = Depends(get_db)) -> AbstractUserRepository:
    return cast(AbstractUserRepository, SQLAlchemyUserRepository(session))

async def get_password_hasher() -> AbstractPasswordHasher:
    return cast(AbstractPasswordHasher, BCryptPasswordHasher())

async def get_token_provider() -> AbstractTokenProvider:
    return cast(AbstractTokenProvider, JWTTokenProvider(settings.JWT_SECRET_KEY))

async def get_avatar_storage() -> AbstractFileStorage:
    storage = MinIOFileStorage(settings.MINIO_AVATAR_BUCKET)
    return cast(AbstractFileStorage, storage)

async def get_avatar_provider() -> AbstractAvatarProvider:
    return cast(AbstractAvatarProvider, DiceBearBotttsProvider())

async def get_image_processor() -> AbstractImageProcessor:
    return cast(AbstractImageProcessor, PillowImageProcessor())


# WebRTC
async def get_clickhouse_client() -> ClickHouseAsyncClient:
    client = ClickHouseAsyncClient()
    await client.initialize()
    return client

async def get_vector_repository(
    clickhouse_client: ClickHouseAsyncClient = Depends(get_clickhouse_client)
) -> AbstractVectorRepository:
    return cast(AbstractVectorRepository, ClickHouseVectorRepository(clickhouse_client))

async def get_webrtc_manager() -> AbstractWebRTCManager:
    return cast(AbstractWebRTCManager, WebRTCManagerImpl())

async def get_vectorizer() -> AbstractVectorizer:
    from app.infrastructure.external.sentence_transformer_vectorizer import SentenceTransformerVectorizer
    vectorizer = SentenceTransformerVectorizer()
    await vectorizer.warmup()
    return cast(AbstractVectorizer, vectorizer)


async def get_initiate_connection_use_case(
    webrtc_manager: AbstractWebRTCManager = Depends(get_webrtc_manager),
    vector_repo: AbstractVectorRepository = Depends(get_vector_repository),
    user_repo: AbstractUserRepository = Depends(get_user_repo),
    vectorizer: AbstractVectorizer = Depends(get_vectorizer),
) -> InitiateConnectionUseCase:
    return cast(
        InitiateConnectionUseCase,
        InitiateConnectionUseCaseImpl(
            webrtc_manager=webrtc_manager,
            vector_repo=vector_repo,
            user_repo=user_repo,
            vectorizer=vectorizer
        )
    )

async def get_handle_answer_use_case(
    webrtc_manager: AbstractWebRTCManager = Depends(get_webrtc_manager)
) -> HandleAnswerUseCase:
    return cast(
        HandleAnswerUseCase,
        HandleAnswerUseCaseImpl(
            webrtc_manager=webrtc_manager
        )
    )

async def get_webrtc_output_port(
    initiate_use_case: InitiateConnectionUseCase = Depends(get_initiate_connection_use_case),
    handle_answer_use_case: HandleAnswerUseCase = Depends(get_handle_answer_use_case)
) -> WebRTCOutputPort:
    
    class CompositeWebRTCPort(WebRTCOutputPort):
        async def initiate_connection(self, **kwargs):
            return await initiate_use_case.execute(**kwargs)
        
        async def handle_answer(self, **kwargs):
            return await handle_answer_use_case.execute(**kwargs)
    
    return cast(WebRTCOutputPort, CompositeWebRTCPort())


async def get_initiate_connection_func(
    webrtc_port: WebRTCOutputPort = Depends(get_webrtc_output_port)
):
    return webrtc_port.initiate_connection

async def get_handle_answer_func(
    webrtc_port: WebRTCOutputPort = Depends(get_webrtc_output_port)
):
    return webrtc_port.handle_answer

async def shutdown_webrtc():
    webrtc_manager = await get_webrtc_manager()
    await webrtc_manager.shutdown()



async def get_register_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repo),
    password_hasher: AbstractPasswordHasher = Depends(get_password_hasher),
    avatar_storage: AbstractFileStorage = Depends(get_avatar_storage),
    avatar_provider: AbstractAvatarProvider = Depends(get_avatar_provider),
    image_processor: AbstractImageProcessor = Depends(get_image_processor),
) -> RegisterUserUseCase:
    return cast(
        RegisterUserUseCase,
        RegisterUserUseCaseImpl(
            user_repo=user_repo,
            password_hasher=password_hasher,
            avatar_provider=avatar_provider,
            avatar_storage=avatar_storage,
            image_processor=image_processor,
            default_avatar_filename="default_avatar.jpg"
        )
    )

async def get_login_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repo),
    password_hasher: AbstractPasswordHasher = Depends(get_password_hasher),
    token_provider: AbstractTokenProvider = Depends(get_token_provider),
) -> LoginUserUseCase:
    return cast(
        LoginUserUseCase,
        LoginUserUseCaseImpl(
            user_repo=user_repo,
            password_hasher=password_hasher,
            token_provider=token_provider
        )
    )

async def get_user_profile_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repo),
) -> GetUserProfileUseCase:
    return cast(
        GetUserProfileUseCase,
        GetUserProfileUseCaseImpl(user_repo=user_repo)
    )

async def get_update_profile_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repo),
) -> UpdateUserProfileUseCase:
    return cast(
        UpdateUserProfileUseCase,
        UpdateUserProfileUseCaseImpl(user_repo=user_repo)
    )

async def get_upload_avatar_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repo),
    avatar_storage: AbstractFileStorage = Depends(get_avatar_storage),
    image_processor: AbstractImageProcessor = Depends(get_image_processor),
) -> UploadUserAvatarUseCase:
    return cast(
        UploadUserAvatarUseCase,
        UploadUserAvatarUseCaseImpl(
            user_repo=user_repo,
            avatar_storage=avatar_storage,
            image_processor=image_processor
        )
    )

async def get_load_avatar_use_case(
    user_repo: AbstractUserRepository = Depends(get_user_repo),
    avatar_storage: AbstractFileStorage = Depends(get_avatar_storage),
) -> LoadUserAvatarUseCase:
    return cast(
        LoadUserAvatarUseCase,
        LoadUserAvatarUseCaseImpl(
            user_repo=user_repo,
            avatar_storage=avatar_storage
        )
    )
