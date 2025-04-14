from typing import Any, Dict

from logger import logger
from handlers.hobbies import handle_event_hobbies, handle_event_hobby
from handlers.users import handle_event_create_user, handle_event_get_user, handle_event_get_user_info


async def handle_event_distribution(body: Dict[str, Any]) -> None:
    match body['action']:
        case 'get_hobbies':
            await handle_event_hobbies(body)
            return
        case 'create_hobby':
            await handle_event_hobby(body)
            return
        case 'create_user':
            await handle_event_create_user(body)
            return
        case 'get_user':
            await handle_event_get_user(body)
            return
        case 'get_user_info':
            await handle_event_get_user_info(body)