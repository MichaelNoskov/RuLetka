from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.middleware.security import SecurityMiddleware
from app.exceptions.handlers import add_exception_handlers

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

app.add_middleware(SecurityMiddleware)

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
