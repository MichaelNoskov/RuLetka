
from fastapi import Request, APIRouter, Depends, HTTPException, status, UploadFile, File

from app.api.schemas.requests.user import UserInfo
from app.api.schemas.responses.user import UserResponse
from app.api.dependencies import get_user_service


def get_current_user_id(request: Request) -> int:
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


router = APIRouter()


@router.get("/user", response_model=UserResponse)
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    user_service=Depends(get_user_service)
):
    user = await user_service.get_profile(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return UserResponse.from_domain(user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserInfo,
    user_id: int = Depends(get_current_user_id),
    user_service=Depends(get_user_service)
):

    existing_user = await user_service.get_by_username(user_data.username)
    if existing_user and existing_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Имя пользователя уже занято"
        )

    updated_user = await user_service.update_profile(user_id, user_data)
    return UserResponse.from_domain(updated_user)


@router.post("/profile/image", status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    user_service=Depends(get_user_service)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением"
        )

    try:
        contents = await file.read()
        avatar_url = await user_service.upload_avatar(user_id, contents)

        return {
            "avatar_url": avatar_url,
            "message": "Фото профиля успешно загружено"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не получилось загрузить аватар"
        )
