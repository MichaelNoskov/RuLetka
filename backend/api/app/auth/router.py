from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from common.schemas.user import UserRegister, UserLogin
from app.utils import create_jwt_token, encode_password, check_password
from common.core.config import settings
from common.storage.rabbit import send_message
from fastapi import status
from uuid import uuid4
from datetime import datetime, timedelta, timezone

router = APIRouter()

# Временная "база данных" пользователейSRegister
fake_users_db = {
    "user1": {
        "username": "user1",
        "password": "password1"  # В реальном приложении хранить хеш
    }
}


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister) -> UserLogin | dict:
    data.password = encode_password(data.password)
    data.birthdate = data.birthdate.isoformat()

    user_id = str(uuid4())
    msg = {'user_id': user_id, 'action': 'create_user', 'new_user': data.model_dump()}

    try:
        answer = await send_message(msg, 'users', user_id, True)
        info: UserLogin = UserLogin.model_validate_json(answer)
        return info
    except Exception as exc:
        raise HTTPException(status_code=403, detail="Пользователь с таким именем уже существует")


@router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user_id = str(uuid4())
    msg = {'user_id': user_id, 'action': 'get_user', 'username': form_data.username}
    try:
        answer = await send_message(msg, 'users', user_id, True)
        user: UserLogin = UserLogin.model_validate_json(answer)
    except Exception as exc:
        raise HTTPException(status_code=403, detail="Некорректные учётные данные")

    if not check_password(form_data.password, user.password):
        raise HTTPException(status_code=403, detail="Некорректные учётные данные")
    
    token = create_jwt_token({"sub": str(user.id)})

    response.set_cookie(
        key=settings.COOKIE_NAME,
        expires=datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        value=token,
        samesite="Lax",
    )
    
    return {"message": "Успешный вход"}
