from fastapi import APIRouter, Depends, Form
from common.schemas.hobbies import HobbySchema, HobbyCreate, HobbyList
from common.schemas.user import UserInfo
from common.storage.rabbit import send_message
from uuid import uuid4
from app.utils import get_user_id
from pydantic.types import PastDate
from common.core.config import settings

router = APIRouter()


@router.post("/hobbies/")
async def create_hobby(
    hobby: HobbyCreate,
) -> HobbySchema | dict:

    user_id = str(uuid4())
    body = {'user_id': user_id, 'action': 'create_hobby', 'new_hobby': hobby.model_dump()}

    try:
        answer = await send_message(body, settings.DB_QUEUE, 'hobbies', user_id, wait_answer=True)
        info: HobbySchema = HobbySchema.model_validate_json(answer)
        return info
    except Exception as exc:
        return {'Error': 'Попробуйте позже, ме ещё не подключили базу данных)))'}


@router.get("/hobbies/")
async def read_hobbies() -> HobbyList | dict:

    user_id = str(uuid4())
    body = {'user_id': user_id, 'action': 'get_hobbies'}

    try:
        answer = await send_message(body, settings.DB_QUEUE, 'hobbies', user_id, wait_answer=True)
        info: HobbyList = HobbyList.model_validate_json(answer)
        return info
    except Exception as exc:
        return {'Error': 'Попробуйте позже, ме ещё не подключили базу данных)))'}


@router.get("/user/")
async def get_userdata(user_id: str = Depends(get_user_id)) -> UserInfo | dict:

    body = {'user_id': user_id, 'action': 'get_user_info'}

    try:
        answer = await send_message(body, settings.DB_QUEUE, 'users', user_id, wait_answer=True)
        info: UserInfo = UserInfo.model_validate_json(answer)
        return info
    except Exception as exc:
        return {'Error': 'Попробуйте позже, ме ещё не подключили базу данных)))'}
    


@router.post("/user/")
async def update_userdata(username: str = Form(...),
    is_male: bool = Form(...),
    birthdate: PastDate = Form(...),
    country: str = Form(...),
    description: str = Form(...),
    user_id: str = Depends(get_user_id)
) -> UserInfo | dict:
    
    info = UserInfo(
        username=username,
        is_male=is_male,
        birthdate=birthdate,
        country=country,
        description=description
    )

    info.birthdate = info.birthdate.isoformat()

    body = {'user_id': user_id, 'action': 'set_user_info', 'new_info': info.model_dump()}

    # try:
    answer = await send_message(body, settings.DB_QUEUE, 'users', user_id, wait_answer=True)
    info: UserInfo = UserInfo.model_validate_json(answer)
    return info
    # except Exception as exc:
    #     return {'Error': exc}
