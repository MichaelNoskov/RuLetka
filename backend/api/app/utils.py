from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from common.core.config import settings
from bcrypt import checkpw, gensalt, hashpw
from fastapi import Request, HTTPException


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def encode_password(password: str) -> str:
    salt = gensalt()
    password: bytes = password.encode()
    
    return hashpw(password, salt).decode()

def check_password(new_password: str, hashed_password: str) -> bool:
    new_password: bytes = new_password.encode()
    
    return checkpw(new_password, hashed_password.encode('utf-8'))

async def get_user_id(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Получен некорректный токен авторизации")
        return user_id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Получен некорректный токен авторизации")
