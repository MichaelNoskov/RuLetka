from fastapi import APIRouter, Depends
from common.schemas.hobbies import HobbySchema, HobbyCreate, HobbyList
from common.schemas.user import UserInfo
from common.storage.rabbit import send_message
from uuid import uuid4
from app.utils import get_user_id

router = APIRouter()


@router.post("/hobbies/")
async def create_hobby(
    hobby: HobbyCreate,
) -> HobbySchema | dict:

    user_id = str(uuid4())
    body = {'user_id': user_id, 'action': 'create_hobby', 'new_hobby': hobby.model_dump()}

    try:
        answer = await send_message(body, 'hobbies', user_id, wait_answer=True)
        info: HobbySchema = HobbySchema.model_validate_json(answer)
        return info
    except Exception as exc:
        return {'Error': 'Попробуйте позже, ме ещё не подключили базу данных)))'}


@router.get("/hobbies/")
async def read_hobbies() -> HobbyList | dict:

    user_id = str(uuid4())
    body = {'user_id': user_id, 'action': 'get_hobbies'}

    try:
        answer = await send_message(body, 'hobbies', user_id, wait_answer=True)
        info: HobbyList = HobbyList.model_validate_json(answer)
        return info
    except Exception as exc:
        return {'Error': 'Попробуйте позже, ме ещё не подключили базу данных)))'}


@router.get("/user/")
async def update_user(user_id: str = Depends(get_user_id)) -> UserInfo | dict:

    body = {'user_id': user_id, 'action': 'get_user_info'}

    try:
        answer = await send_message(body, 'users', user_id, wait_answer=True)
        info: UserInfo = UserInfo.model_validate_json(answer)
        return info
    except Exception as exc:
        return {'Error': 'Попробуйте позже, ме ещё не подключили базу данных)))'}
