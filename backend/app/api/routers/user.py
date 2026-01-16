from fastapi import Request, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.api.schemas.requests.user import UserInfo
from app.api.schemas.responses.user import UserResponse
from app.core.ports.usecases.user import (
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
    UploadUserAvatarUseCase,
    LoadUserAvatarUseCase
)
from app.infrastructure.web.dependencies import (
    get_user_profile_use_case,
    get_update_profile_use_case,
    get_upload_avatar_use_case,
    get_load_avatar_use_case
)

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
    result = await use_case.execute(user_id)
    return UserResponse(**result)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserInfo,
    user_id: int = Depends(get_current_user_id),
    update_use_case: UpdateUserProfileUseCase = Depends(get_update_profile_use_case),
    get_use_case: GetUserProfileUseCase = Depends(get_user_profile_use_case)
):
    existing_user_result = await get_use_case.execute_by_username(user_data.username)
    if existing_user_result and existing_user_result.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Имя пользователя уже занято"
        )
    
    result = await update_use_case.execute(
        user_id=user_id,
        username=user_data.username,
        is_male=user_data.is_male,
        birthdate=user_data.birthdate,
        country=user_data.country,
        description=user_data.description
    )

    return UserResponse(**result)


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
    
    await use_case.execute(user_id, contents)

    return {
        "message": "Фото профиля успешно загружено"
    }
