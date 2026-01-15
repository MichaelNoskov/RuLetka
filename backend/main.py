from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.experience import router as expirience_router
from app.api.middleware import setup_security_middleware
from app.infrastructure.adapters.repositories.jwt_provider import JWTTokenProvider
from app.infrastructure.config.settings import settings
from app.exceptions.handlers import add_exception_handlers

app = FastAPI()
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
