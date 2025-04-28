from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from common.storage.database import async_session
from common.storage.rabbit import send_answer
from common.storage.models.hobby import Hobby
from common.schemas.hobbies import HobbyList, HobbySchema


async def handle_event_hobbies(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')
    async with async_session() as db:

        result = await db.execute(select(Hobby))
        hobby_list = HobbyList(hobbies=[
            HobbySchema.model_validate(hobby.__dict__) for hobby in result.scalars().all()
        ])

    serialized_data = hobby_list.model_dump_json().encode('utf-8')

    await send_answer(serialized_data, "hobbies", user_id)


async def handle_event_hobby(body: Dict[str, Any]) -> None:
    user_id = body.get('user_id')

    async with async_session() as db:

        new_hobby = Hobby(
            **body.get('new_hobby')
        )
        db.add(new_hobby)

        success = False
        try:
            await db.commit()
            success = True            
        except IntegrityError:
            await db.rollback()
        
    if success:
        hobby = HobbySchema.model_validate(new_hobby.__dict__)
        serialized_data = hobby.model_dump_json().encode('utf-8')
        await send_answer(serialized_data, "hobbies", user_id)
