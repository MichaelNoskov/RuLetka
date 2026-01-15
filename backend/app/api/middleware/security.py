from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from app.infrastructure.config.settings import settings
from app.infrastructure.adapters.auth import verify_token


class SecurityMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app):
        super().__init__(app)
        self.public_paths = [
            '/docs',
            '/openapi.json',
            '/auth/login',
            '/auth/register',
            '/api/hobbies',
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        if request.url.path in self.public_paths:
            return await call_next(request)

        token = request.cookies.get(settings.COOKIE_NAME)
        
        try:
            payload = verify_token(token)
            # request.state.user_roles = payload.get("roles", [])
            # request.state.user_id = payload.get("sub")
            # request.state.permissions = []
            # for role in request.state.user_roles:
            #     request.state.permissions.extend(ROLE_PERMISSIONS.get(role, []))
            
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'Error': 'Необходима авторизация'}
            )
        
        return await call_next(request)
