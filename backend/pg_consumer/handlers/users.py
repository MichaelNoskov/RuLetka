from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from common.storage.database import async_session
from common.storage.rabbit import send_answer
from common.storage.models.user import User
from common.schemas.user import UserRegister, UserLogin, UserInfo


async def handle_event_create_user(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    async with async_session() as db:

        new_user = User(
            **UserRegister(**body.get('new_user')).__dict__
        )
        db.add(new_user)

        success = False
        try:
            await db.commit()
            success = True            
        except IntegrityError:
            await db.rollback()
        
    if success:
        new_user = UserLogin.model_validate(new_user.__dict__)
        serialized_data = new_user.model_dump_json().encode('utf-8')
        await send_answer(serialized_data, "users", user_id)


async def handle_event_get_user(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    username = body.get('username')
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
    
    serialized_data = {}
    if user:
        user = UserLogin.model_validate(user.__dict__)
        serialized_data = user.model_dump_json().encode('utf-8')
    await send_answer(serialized_data, "users", user_id)


async def handle_event_get_user_info(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

    serialized_data = {}
    if user:
        user = UserInfo.model_validate(user.__dict__)
        serialized_data = user.model_dump_json().encode('utf-8')
    await send_answer(serialized_data, "users", user_id)
