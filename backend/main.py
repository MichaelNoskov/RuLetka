from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.user import router as user_router
from app.infrastructure.web.middleware.security import AuthenticationMiddleware
from app.infrastructure.config.settings import settings
from app.api.exceptions.handlers import register_exception_handlers
from app.infrastructure.initializers.static_resource_initializer import StaticResourceInitializer


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск инициализации приложения...", flush=True)
    
    try:
        static_initializer = StaticResourceInitializer()
        static_initializer.initialize()
        
        print("Статические ресурсы инициализированы", flush=True)
        
    except Exception as e:
        print(f"Ошибка при инициализации: {e}", flush=True)
    
    yield

    print("Приложение завершает работу...", flush=True)


app = FastAPI(lifespan=lifespan)

app.add_middleware(AuthenticationMiddleware)

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

register_exception_handlers(app)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/api", tags=["user"])
