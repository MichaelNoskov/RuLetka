from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.infrastructure.adapters.services.jwt_token_provider import JWTTokenProvider
from app.infrastructure.config.settings import settings


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        public_paths = [
            "/auth", 
            "/health", 
            "/docs", 
            "/redoc", 
            "/openapi.json",
            "/static"
        ]
        
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        token = request.cookies.get(settings.COOKIE_NAME)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Необходима авторизация"}
            )
        
        try:
            token_provider = JWTTokenProvider(
                secret_key=settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM
            )
            payload = token_provider.verify(token)
            request.state.user_id = int(payload["sub"])
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Токен не валиден'}
            )
        
        return await call_next(request)
