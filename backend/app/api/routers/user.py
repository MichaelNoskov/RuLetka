from fastapi import Request, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.api.schemas.requests.user import UserInfo
from app.api.schemas.responses.user import UserResponse
from app.application.use_cases.user.get_user_profile import GetUserProfileUseCase
from app.application.use_cases.user.update_user_profile import UpdateUserProfileUseCase
from app.application.use_cases.user.upload_user_avatar import UploadUserAvatarUseCase
from app.application.use_cases.user.load_user_avatar import LoadUserAvatarUseCase
from app.infrastructure.web.dependencies import (
    get_user_profile_use_case,
    get_update_profile_use_case,
    get_upload_avatar_use_case,
    get_load_avatar_use_case
)
from app.application.mappers.user_mapper import UserMapper

router = APIRouter()


def get_current_user_id(request: Request) -> int:
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


@router.get("/user", response_model=UserResponse)
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    use_case: GetUserProfileUseCase = Depends(get_user_profile_use_case)
):
    user = await use_case.execute(user_id)
    return UserResponse(**UserMapper.to_response(user))


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserInfo,
    user_id: int = Depends(get_current_user_id),
    update_use_case: UpdateUserProfileUseCase = Depends(get_update_profile_use_case),
    get_use_case: GetUserProfileUseCase = Depends(get_user_profile_use_case)
):
    existing_user = await get_use_case.execute_by_username(user_data.username)
    if existing_user and existing_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Имя пользователя уже занято"
        )

    from app.application.dto.user import UserUpdateDTO
    dto = UserUpdateDTO(
        username=user_data.username,
        is_male=user_data.is_male,
        birthdate=user_data.birthdate,
        country=user_data.country,
        description=user_data.description
    )
    
    updated_user = await update_use_case.execute(user_id, dto)
    return UserResponse(**UserMapper.to_response(updated_user))


@router.get("/profile/image")
async def get_avatar(
    user_id: int = Depends(get_current_user_id),
    use_case: LoadUserAvatarUseCase = Depends(get_load_avatar_use_case)
):
    image_bytes = await use_case.execute(user_id)
    
    return StreamingResponse(
        BytesIO(image_bytes),
        media_type='image/jpeg',
        headers={'Content-Disposition': 'inline; filename="avatar.jpeg"'}
    )


@router.post("/profile/image", status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    use_case: UploadUserAvatarUseCase = Depends(get_upload_avatar_use_case)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением"
        )

    contents = await file.read()

    from app.application.dto.user import AvatarUploadDTO
    dto = AvatarUploadDTO(
        user_id=user_id,
        image_bytes=contents
    )
    
    avatar_url = await use_case.execute(dto)

    return {
        "avatar_url": avatar_url,
        "message": "Фото профиля успешно загружено"
    }
