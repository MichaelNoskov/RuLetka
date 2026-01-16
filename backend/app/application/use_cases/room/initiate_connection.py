from dataclasses import dataclass
from typing import Dict, Any, Optional
import random
from datetime import date

from app.core.ports.services.webrtc_manager import AbstractWebRTCManager
from app.core.ports.repositories.vector_repository import AbstractVectorRepository
from app.core.ports.repositories.user_repository import AbstractUserRepository
from app.core.ports.services.vectorizer import AbstractVectorizer
from app.core.ports.usecases.webrtc import InitiateConnectionUseCase


@dataclass
class InitiateConnectionUseCaseImpl(InitiateConnectionUseCase):
    webrtc_manager: AbstractWebRTCManager
    vector_repo: AbstractVectorRepository
    user_repo: AbstractUserRepository
    vectorizer: AbstractVectorizer
    
    async def execute(
        self,
        user_id: str,
        gender_filter: Optional[bool] = None,
        age_filter: Optional[int] = None,
        country_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Полная логика инициализации соединения:
        1. Создать WebRTC соединение (получить SDP + временный ID)
        2. Получить информацию о пользователе
        3. Сгенерировать вектор эмбеддинга
        4. Найти/создать комнату
        5. Переместить соединение в комнату
        6. Вернуть результат
        """
        
        # 1. Создаем WebRTC соединение
        sdp_data, temp_id = await self.webrtc_manager.initiate_connection(
            user_id=user_id,
            gender_filter=gender_filter,
            age_filter=age_filter,
            country_filter=country_filter
        )
        
        # 2. Получаем информацию о пользователе
        user = await self.user_repo.get_by_id(int(user_id))
        if not user:
            # Очищаем временное соединение если пользователь не найден
            raise ValueError(f"User {user_id} not found")
        
        # 3. Генерируем эмбеддинг из описания
        vector = self.vectorizer.generate_embedding(user.description)
        
        # 4. Рассчитываем возраст пользователя
        today = date.today()
        user_age = today.year - user.birthdate.year
        if (today.month, today.day) < (user.birthdate.month, user.birthdate.day):
            user_age -= 1
        
        # 5. Преобразуем фильтры
        gender_str = None
        if gender_filter is not None:
            gender_str = "male" if gender_filter else "female"
        elif user.is_male is not None:
            gender_str = "male" if user.is_male else "female"
        
        # 6. Ищем подходящую комнату
        available_rooms = await self.vector_repo.search_rooms(
            query_vector=vector,
            gender=gender_str,
            age=age_filter if age_filter else user_age,
            country=country_filter if country_filter else user.country
        )
        
        # 7. Определяем room_id
        if available_rooms:
            # Нашли комнату - присоединяемся
            room_id = random.choice(available_rooms)
            await self.vector_repo.delete_room(room_id)
        else:
            # Комнаты нет - создаем новую
            room_id = user_id
            
            # Сохраняем пользователя для поиска
            await self.vector_repo.save_user_vector(
                user_id=user_id,
                vector=vector,
                gender=gender_str,
                age=age_filter if age_filter else user_age,
                country=country_filter if country_filter else user.country
            )
        
        # 8. Перемещаем соединение в комнату и получаем постоянный client_id
        client_id = await self.webrtc_manager.move_connection_to_room(
            temp_id=temp_id,
            room_id=room_id
        )
        
        # 9. Формируем ответ в формате микросервиса
        return {
            "sdp": sdp_data["sdp"],
            "type": sdp_data["type"],
            "id": client_id,
            "room_id": room_id
        }
