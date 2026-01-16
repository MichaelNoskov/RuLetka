from fastapi import APIRouter, Depends, Response
from datetime import datetime, timedelta, timezone

from app.api.schemas.requests.user import UserRegister, UserLogin
from app.api.schemas.responses.user import UserResponse
from app.application.use_cases.auth.register_user import RegisterUserUseCase
from app.application.use_cases.auth.login_user import LoginUserUseCase
from app.infrastructure.web.dependencies import get_register_use_case, get_login_use_case
from app.infrastructure.config.settings import settings
from app.application.mappers.user_mapper import UserMapper

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    use_case: RegisterUserUseCase = Depends(get_register_use_case)
):
    from app.application.dto.user import UserCreateDTO
    dto = UserCreateDTO(
        username=user_data.username,
        password=user_data.password,
        is_male=user_data.is_male,
        birthdate=user_data.birthdate,
        country=user_data.country,
        description=user_data.description
    )

    domain_user = await use_case.execute(dto)

    return UserResponse(**UserMapper.to_response(domain_user))


@router.post("/login", response_model=UserResponse) 
async def login(
    credentials: UserLogin,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
    response: Response = None
):
    from app.application.dto.auth import LoginDTO
    dto = LoginDTO(
        username=credentials.username,
        password=credentials.password
    )

    user, token = await use_case.execute(dto)

    response.set_cookie(
        key=settings.COOKIE_NAME,
        expires=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        value=token,
        samesite="Lax",
        httponly=True,
        secure=settings.HTTPS_ONLY
    )

    return UserResponse(**UserMapper.to_response(user))


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key=settings.COOKIE_NAME, path="/")
    return {"message": "Успешный выход"}
