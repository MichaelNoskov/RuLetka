from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.expirience.router import router as hobbies_router
from app.rooms.router import router as rooms_router

from app.utils import verify_token
from common.core.config import settings

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(hobbies_router, prefix="/api")
app.include_router(rooms_router, prefix='/room')


@app.middleware('http')
async def security_middleware(request: Request, handler: Callable):
    # try:
        public_paths = [
            '/docs',
            '/openapi.json',
            '/auth/login',
            '/auth/register',
            '/api/hobbies',
        ]
        if request.url.path in public_paths:
            return await handler(request)

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
        return await handler(request)

    # except Exception as exc:
    #     return JSONResponse(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content={'Error': 'Internal server error...'}
    #     )


origins = [
    f"http://{settings.BACKEND_HOST}:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return "Hello, World!"
