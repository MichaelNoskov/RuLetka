from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    DomainError, UsernameTooShortError, UserAlreadyExistsError,
    UserNotFoundError, InvalidPasswordError, NotAuthenticatedError, NotFound
)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UsernameTooShortError)
    async def username_too_short_handler(request: Request, exc: UsernameTooShortError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(InvalidPasswordError)
    async def invalid_password_handler(request: Request, exc: InvalidPasswordError):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(NotAuthenticatedError)
    async def not_authenticated_handler(request: Request, exc: NotAuthenticatedError):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(NotFound)
    async def not_found_handler(request: Request, exc: NotFound):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
