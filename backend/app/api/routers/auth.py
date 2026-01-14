from fastapi import APIRouter, Depends
from app.api.schemas.requests.user import UserRegister, UserLogin
from app.api.schemas.responses.user import UserResponse
from app.api.dependencies import get_user_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, service=Depends(get_user_service)):
    domain_user = await service.register(user_data)
    return UserResponse.from_domain(domain_user)


@router.post("/login", response_model=UserResponse) 
async def login(credentials: UserLogin, service=Depends(get_user_service)):
    return await service.login(credentials.username, credentials.password)
