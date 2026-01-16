from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.user import router as user_router
from app.api.routers.room import router as room_router
from app.api.exceptions.handlers import register_exception_handlers
from app.infrastructure.web.middleware.security import AuthenticationMiddleware
from app.infrastructure.initializers.static_resource_initializer import StaticResourceInitializer
from app.infrastructure.adapters.repositories.clickhouse_vector_repository import ClickHouseVectorRepository
from app.infrastructure.storage.clickhouse_client import ClickHouseAsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск инициализации приложения...", flush=True)

    clickhouse_client = ClickHouseAsyncClient()
    app.state.clickhouse_client = clickhouse_client
    
    try:
        static_initializer = StaticResourceInitializer()
        static_initializer.initialize()
        
        print("Статические ресурсы инициализированы", flush=True)
        
    except Exception as e:
        print(f"Ошибка при инициализации: {e}", flush=True)
    
    yield

    if hasattr(app.state, 'clickhouse_client'):
        await app.state.clickhouse_client.close()

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
app.include_router(room_router, prefix="/room", tags=["room"])
