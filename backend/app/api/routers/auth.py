from fastapi import APIRouter, Depends, Response
from datetime import datetime, timedelta, timezone

from app.api.schemas.requests.user import UserRegister, UserLogin
from app.api.schemas.responses.user import UserResponse
from app.api.dependencies import get_user_service, get_token_provider
from app.infrastructure.config.settings import settings
from app.infrastructure.config.settings import settings


router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, service=Depends(get_user_service)):
    domain_user = await service.register(user_data)
    return UserResponse.from_domain(domain_user)


@router.post("/login", response_model=UserResponse) 
async def login(
    credentials: UserLogin,
    user_service=Depends(get_user_service),
    token_provider=Depends(get_token_provider),
    response: Response = None
):
    # TODO: вынести в usecase
    user = await user_service.login(credentials.username, credentials.password)
    token = token_provider.create(str(user.id))
    response.set_cookie(
        key=settings.COOKIE_NAME,
        expires=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        value=token,
        samesite="Lax",
        httponly=True,
        secure=False  # TODO: вынести в конфиг
    )

    return UserResponse.from_domain(user)


@router.get("/logout")
async def logout(
    response: Response,
):
    # TODO: вынести в usecase
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/"
    )
    
    return {
        "message": "Успешный выход",
    }
