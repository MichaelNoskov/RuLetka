from fastapi import APIRouter, Depends, Response
from datetime import datetime, timedelta, timezone

from app.api.schemas.requests.user import UserRegister, UserLogin
from app.api.schemas.responses.user import UserResponse
from app.core.ports.usecases.auth import LoginUserUseCase, RegisterUserUseCase
from app.infrastructure.web.dependencies import get_register_use_case, get_login_use_case
from app.infrastructure.config.settings import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    use_case: RegisterUserUseCase = Depends(get_register_use_case)
):
    result = await use_case.execute(
        username=user_data.username,
        password=user_data.password,
        is_male=user_data.is_male,
        birthdate=user_data.birthdate,
        country=user_data.country,
        description=user_data.description or ""
    )

    return UserResponse(**result)


@router.post("/login")
async def login(
    credentials: UserLogin,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
    response: Response = None
):
    result = await use_case.execute(
        username=credentials.username,
        password=credentials.password
    )

    token = result.pop("token")

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.HTTPS_ONLY,
        samesite="Lax",
        expires=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "user": UserResponse(**result),
        "token": token
    }


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key=settings.COOKIE_NAME, path="/")
    return {"message": "Успешный выход"}
