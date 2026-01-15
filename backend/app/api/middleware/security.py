from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from app.domain.ports.token_provider import AbstractTokenProvider
from app.domain.ports.user_repository import AbstractUserRepository
from app.infrastructure.config.settings import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    
    def __init__(
        self,
        app,
        token_provider: AbstractTokenProvider,
        user_repository: AbstractUserRepository,
        public_paths: list[str] = None
    ):
        super().__init__(app)
        self.token_provider = token_provider
        self.user_repository = user_repository
        self.public_paths = public_paths or [
            '/docs',
            '/openapi.json',
            '/auth/login',
            '/auth/register',
            '/api/hobbies',
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in self.public_paths:
            return await call_next(request)

        token = self._get_token_from_request(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Необходима авторизация"}
            )
        
        try:
            payload = self.token_provider.verify(token)
            user_id = int(payload.get("sub"))
            # request.state.user_roles = payload.get("roles", [])
            # request.state.user_id = payload.get("sub")
            # request.state.permissions = []
            # for role in request.state.user_roles:
            #     request.state.permissions.extend(ROLE_PERMISSIONS.get(role, []))
            
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Токен не валиден'}
            )

        # user = await self.user_repository.get_by_id(user_id)
        # if not user:
        #     return JSONResponse(
        #         status_code=401,
        #         content={"detail": "Пользователь не найден"}
        #     )
        
        request.state.user_id = user_id
        
        return await call_next(request)

    def _get_token_from_request(self, request: Request) -> str | None:
        token = request.cookies.get(settings.COOKIE_NAME)
        if token:
            return token

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]

        return None
