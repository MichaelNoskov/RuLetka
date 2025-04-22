from typing import Any, Dict

from handlers.handle_event_model import handle_event_generate_vector, handle_event_get_best


async def handle_event_distribution(body: Dict[str, Any]) -> None:
    match body['action']:
        case 'create_user':
            await handle_event_generate_vector(body)
            return
        case 'get_best':
            await handle_event_get_best(body)
            return
