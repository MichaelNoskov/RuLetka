from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.api.dependencies import get_user_service


# TODO: вынести куда-нибудь
def get_current_user_id(request: Request) -> int:
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


router = APIRouter()


@router.get("/avatar")
async def get_file(
    user_id: int = Depends(get_current_user_id),
    user_service = Depends(get_user_service)
):
    image_bytes = await user_service.load_avatar(user_id)
    
    if not image_bytes:
        raise HTTPException(status_code=404, detail="File not found")
    
    filename = "avatar.jpeg"
    extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    content_types = {
        'jpeg': 'image/jpeg',
    }
    
    content_type = content_types.get(extension, 'application/octet-stream')
    
    return StreamingResponse(
        BytesIO(image_bytes),
        media_type=content_type,
        headers={
            'Content-Disposition': f'inline; filename="{filename}"'
        }
    )
