from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.experience import router as expirience_router
from app.api.middleware import setup_security_middleware
from app.infrastructure.adapters.repositories.jwt_provider import JWTTokenProvider
from app.infrastructure.external.fs_static_file_loader import FileSystemStaticFileLoader
from app.infrastructure.adapters.repositories.minio_file_storage import MinIOFileStorage
from app.infrastructure.config.settings import settings
from app.services.static_resource_initializer import StaticResourceInitializer
from app.exceptions.handlers import add_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск инициализации приложения...", flush=True)
    
    try:
        static_loader = FileSystemStaticFileLoader(static_dir="static")
        avatar_storage = MinIOFileStorage(bucket_name=settings.MINIO_AVATAR_BUCKET)
        initializer = StaticResourceInitializer(static_loader, avatar_storage)
        
        print("Инициализация дефолтного аватара в MinIO...", flush=True)
        success = await initializer.initialize_default_avatar()
        
        if success:
            print("Дефолтный аватар успешно загружен в MinIO", flush=True)
            app.state.default_avatar_filename = initializer.get_default_avatar_filename()
        else:
            print("Ошибка загрузки дефолтного аватара", flush=True)
            app.state.default_avatar_filename = "default_avatar.jpg"
            
    except Exception as e:
        print(f"Ошибка при инициализации: {e}", flush=True)
        app.state.default_avatar_filename = "default_avatar.jpg"
    
    yield

    print("Приложение завершает работу...", flush=True)


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth")
app.include_router(expirience_router, prefix="/api")

token_provider = JWTTokenProvider(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM
)
setup_security_middleware(
    app=app,
    token_provider=token_provider,
    public_paths=[
        '/docs',
        '/openapi.json',
        '/auth/login',
        '/auth/register',
        '/api/hobbies',
    ]
)

# TODO: вынести в конфиг
origins = [
    "http://192.168.66.247:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)
