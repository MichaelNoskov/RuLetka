from fastapi import FastAPI, HTTPException
from app.domain.exceptions import *

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(UsernameTooShortError)
    async def username_too_short_handler(request, exc: UsernameTooShortError):
        raise HTTPException(status_code=400, detail=str(exc))
    
    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(request, exc: UserAlreadyExistsError):
        raise HTTPException(status_code=409, detail=str(exc))
    
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request, exc: UserNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc))
    
    @app.exception_handler(InvalidPasswordError)
    async def invalid_credentials_handler(request, exc: InvalidPasswordError):
        raise HTTPException(status_code=401, detail=str(exc))
    
    @app.exception_handler(NotAuthenticatedError)
    async def invalid_credentials_handler(request, exc: NotAuthenticatedError):
        raise HTTPException(status_code=401, detail=str(exc))
