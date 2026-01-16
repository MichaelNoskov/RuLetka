import asyncio
import json
import random
import uuid
from typing import Dict, Any, List, Optional, Set, Tuple
import logging

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay

from app.core.ports.services.webrtc_manager import AbstractWebRTCManager

logger = logging.getLogger(__name__)


class WebRTCManagerImpl(AbstractWebRTCManager):
    """
    Полная реализация WebRTC Manager.
    Поддерживает временные соединения до помещения в комнату.
    """
    
    def __init__(self):
        # rooms: {room_id: list[RTCPeerConnection]}
        self.rooms: Dict[str, List[RTCPeerConnection]] = {}
        
        # tracks: {RTCPeerConnection: set[MediaStreamTrack]}
        self.tracks: Dict[RTCPeerConnection, Set[MediaStreamTrack]] = {}
        
        # Временные соединения: {temp_id: RTCPeerConnection}
        self.temporary_connections: Dict[str, RTCPeerConnection] = {}
        
        # relay для мультиплексирования медиа-потоков
        self.relay = MediaRelay()
        
        # Блокировка для thread-safe операций
        self._lock = asyncio.Lock()
        
        logger.info("WebRTCManager инициализирован")
    
    async def initiate_connection(
        self,
        user_id: str,
        gender_filter: Optional[bool] = None,
        age_filter: Optional[int] = None,
        country_filter: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str]:
        """
        Создать WebRTC соединение и вернуть SDP + временный ID
        """
        async with self._lock:
            # Создаем peer connection
            pc = RTCPeerConnection()
            
            # Генерируем временный ID
            temp_id = str(uuid.uuid4())[:8]
            
            # Генерируем постоянный client_id (будет использоваться после помещения в комнату)
            client_id = str(random.randint(0, 100)).rjust(3, '0')
            pc.client_id = client_id
            pc.user_id = user_id
            pc.temp_id = temp_id
            
            logger.info(
                f"Создан peer connection {client_id} (temp: {temp_id}) "
                f"для пользователя {user_id}"
            )
            
            # Сохраняем во временные соединения
            self.temporary_connections[temp_id] = pc
            
            # Создаем data channel для переговоров
            data_channel = pc.createDataChannel('renegotiation')
            pc.data_channel = data_channel
            
            # Настраиваем обработчики data channel
            self._setup_data_channel_handlers(data_channel, pc)
            
            # Добавляем video transceiver
            pc.addTransceiver('video', direction='recvonly')
            
            # Настраиваем обработчики событий peer connection
            self._setup_peer_connection_handlers(pc)
            
            # Создаем SDP offer
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            
            logger.info(f"Создан offer для {client_id} (temp: {temp_id})")
            
            sdp_data = {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
            
            return sdp_data, temp_id
    
    async def move_connection_to_room(
        self,
        temp_id: str,
        room_id: str
    ) -> str:
        """
        Переместить временное соединение в комнату
        """
        async with self._lock:
            if temp_id not in self.temporary_connections:
                raise ValueError(f"Временное соединение {temp_id} не найдено")
            
            pc = self.temporary_connections.pop(temp_id)
            
            # Создаем комнату если её нет
            if room_id not in self.rooms:
                self.rooms[room_id] = []
            
            # Добавляем в комнату
            self.rooms[room_id].append(pc)
            
            # Инициализируем множество треков
            self.tracks[pc] = set()
            
            logger.info(
                f"Peer {pc.client_id} перемещен из temp:{temp_id} в комнату {room_id}"
            )
            
            # Подписываемся на треки других участников комнаты
            for other_pc in self.rooms[room_id]:
                if other_pc != pc:
                    for track in self.tracks.get(other_pc, set()):
                        pc.addTransceiver(
                            self.relay.subscribe(track), 
                            direction='sendonly'
                        )
            
            # Отправляем обновленный список пользователей
            await self._send_user_list(room_id)
            
            return pc.client_id
    
    async def handle_answer(
        self,
        room_id: str,
        client_id: str,
        sdp: str,
        sdp_type: str
    ) -> Dict[str, Any]:
        """Обработать SDP answer от клиента"""
        async with self._lock:
            if room_id not in self.rooms:
                logger.warning(f"Комната {room_id} не найдена")
                return {"error": "Room not found."}
            
            # Ищем peer connection по client_id
            pc = None
            for p in self.rooms[room_id]:
                if hasattr(p, 'client_id') and p.client_id == client_id:
                    pc = p
                    break
            
            if not pc:
                logger.warning(f"Peer connection {client_id} не найден в комнате {room_id}")
                return {"error": "Peer connection not found."}
            
            try:
                # Устанавливаем remote description
                answer = RTCSessionDescription(sdp=sdp, type=sdp_type)
                await pc.setRemoteDescription(answer)
                
                logger.info(f"Answer установлен для {client_id} в комнате {room_id}")
                
                # Отправляем обновленный список пользователей
                await self._send_user_list(room_id)
                
                return {"message": "Connection established."}
                
            except Exception as e:
                logger.error(f"Ошибка установки answer для {client_id}: {e}")
                return {"error": f"Failed to establish connection: {str(e)}"}
    
    async def cleanup_connection(self, client_id: str) -> None:
        """Очистить соединение по client_id"""
        await self._remove_client_by_id(client_id)
    
    async def get_room_users(self, room_id: str) -> List[str]:
        """Получить список пользователей в комнате"""
        async with self._lock:
            if room_id not in self.rooms:
                return []
            
            return [
                pc.client_id for pc in self.rooms[room_id] 
                if hasattr(pc, 'client_id')
            ]
    
    async def shutdown(self) -> None:
        """Закрыть все соединения при shutdown"""
        async with self._lock:
            logger.info("Завершение всех WebRTC соединений...")
            
            # Закрываем временные соединения
            for temp_id, pc in list(self.temporary_connections.items()):
                try:
                    await pc.close()
                    logger.info(f"Закрыто временное соединение {temp_id}")
                except Exception as e:
                    logger.error(f"Ошибка закрытия временного соединения {temp_id}: {e}")
            self.temporary_connections.clear()
            
            # Закрываем соединения в комнатах
            for room_id, connections in list(self.rooms.items()):
                for pc in connections:
                    try:
                        await pc.close()
                        logger.info(f"Закрыто соединение {pc.client_id} в комнате {room_id}")
                    except Exception as e:
                        logger.error(f"Ошибка закрытия соединения {pc.client_id}: {e}")
            
            self.rooms.clear()
            self.tracks.clear()
            logger.info("Все WebRTC соединения закрыты")
    
    async def cleanup_temporary_connections(self, timeout_seconds: int = 30):
        """
        Очистить старые временные соединения
        (вызывать периодически)
        """
        # Реализация по необходимости
        pass
    
    def _setup_data_channel_handlers(self, data_channel, pc: RTCPeerConnection):
        """Настройка обработчиков data channel"""
        
        @data_channel.on("open")
        async def on_open():
            logger.info(f"Data channel открыт для {pc.client_id}")
            
            # Если соединение уже в комнате, отправляем список пользователей
            room_id = self._find_room_for_pc(pc)
            if room_id:
                await self._send_user_list(room_id)
        
        @data_channel.on("message")
        async def on_message(message):
            if message == 'keepalive':
                # keepalive пинг
                try:
                    data_channel.send('keepalive')
                except:
                    pass
                return
            
            try:
                # Обработка SDP переговоров
                offer_data = json.loads(message)
                
                if 'sdp' in offer_data and 'type' in offer_data:
                    await pc.setRemoteDescription(
                        RTCSessionDescription(
                            sdp=offer_data['sdp'], 
                            type=offer_data['type']
                        )
                    )
                    
                    # Создаем answer
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    
                    # Отправляем answer обратно
                    data_channel.send(
                        json.dumps({
                            'action': 'answer',
                            'sdp': pc.localDescription.sdp,
                            'type': pc.localDescription.type,
                        })
                    )
                    
                    logger.info(f"Переговоры завершены для {pc.client_id}")
                    
            except json.JSONDecodeError:
                logger.warning(f"Некорректный JSON от {pc.client_id}: {message}")
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения от {pc.client_id}: {e}")
        
        @data_channel.on("close")
        async def on_close():
            logger.info(f"Data channel закрыт для {pc.client_id}")
    
    def _setup_peer_connection_handlers(self, pc: RTCPeerConnection):
        """Настройка обработчиков событий peer connection"""
        
        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            logger.info(
                f"ICE состояние изменилось для {pc.client_id}: {pc.iceConnectionState}"
            )
            
            if pc.iceConnectionState in ('failed', 'disconnected', 'closed'):
                logger.info(f'Клиент {pc.client_id} отключился')
                await self._remove_client(pc)
        
        @pc.on("track")
        async def on_track(track: MediaStreamTrack):
            if track.kind not in ('video',):
                logger.warning(f"Неподдерживаемый тип трека: {track.kind}")
                return
            
            logger.info(f"Получен {track.kind} трек от {pc.client_id}")
            
            # Сохраняем трек только если соединение в комнате
            if pc in self.tracks:
                self.tracks[pc].add(track)
                
                # Релеим трек другим участникам комнаты
                room_id = self._find_room_for_pc(pc)
                if room_id and room_id in self.rooms:
                    for other_pc in self.rooms[room_id]:
                        if other_pc != pc:
                            # Добавляем трек другим участникам
                            other_pc.addTrack(self.relay.subscribe(track))
                            
                            # Уведомляем о необходимости переговоров
                            if (
                                hasattr(other_pc, 'data_channel') and 
                                other_pc.data_channel.readyState == 'open'
                            ):
                                try:
                                    other_pc.data_channel.send(
                                        json.dumps({'action': 'renegotiating'})
                                    )
                                except:
                                    pass
                            
                            logger.info(f"Трек релеен от {pc.client_id} к {other_pc.client_id}")
    
    def _find_room_for_pc(self, pc: RTCPeerConnection) -> Optional[str]:
        """Найти комнату для peer connection"""
        for room_id, connections in self.rooms.items():
            if pc in connections:
                return room_id
        return None
    
    async def _send_user_list(self, room_id: str) -> None:
        """Отправить список пользователей всем в комнате"""
        if room_id not in self.rooms:
            return
        
        user_ids = [
            pc.client_id for pc in self.rooms[room_id] 
            if hasattr(pc, 'client_id')
        ]
        
        logger.info(f"Отправка списка пользователей комнаты {room_id}: {user_ids}")
        
        for pc in self.rooms[room_id]:
            if (
                hasattr(pc, 'data_channel') and 
                pc.data_channel.readyState == 'open'
            ):
                try:
                    pc.data_channel.send(
                        json.dumps({
                            'action': 'users',
                            'users': user_ids
                        })
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки списка пользователей {pc.client_id}: {e}")
    
    async def _remove_client(self, pc: RTCPeerConnection) -> None:
        """Удалить клиента (из комнаты или временных)"""
        async with self._lock:
            # Проверяем в комнатах
            room_found = False
            for room_id, connections in list(self.rooms.items()):
                if pc in connections:
                    room_found = True
                    
                    # Удаляем из комнаты
                    connections.remove(pc)
                    
                    # Закрываем соединения других участников
                    for other_pc in connections:
                        try:
                            await other_pc.close()
                            if other_pc in self.tracks:
                                del self.tracks[other_pc]
                        except Exception as e:
                            logger.error(f"Ошибка закрытия other_pc: {e}")
                    
                    # Удаляем комнату если она пустая
                    if not connections:
                        del self.rooms[room_id]
                        logger.info(f"Комната {room_id} удалена (пустая)")
                    
                    break
            
            # Проверяем во временных
            temp_id_to_remove = None
            for temp_id, temp_pc in self.temporary_connections.items():
                if temp_pc == pc:
                    temp_id_to_remove = temp_id
                    break
            
            if temp_id_to_remove:
                del self.temporary_connections[temp_id_to_remove]
                logger.info(f"Удалено временное соединение {temp_id_to_remove}")
            
            # Удаляем треки
            if pc in self.tracks:
                del self.tracks[pc]
            
            # Закрываем соединение
            try:
                await pc.close()
                if room_found:
                    logger.info(f"Соединение {pc.client_id} закрыто и удалено из комнаты")
                elif temp_id_to_remove:
                    logger.info(f"Временное соединение {pc.client_id} закрыто")
            except Exception as e:
                logger.error(f"Ошибка закрытия pc {pc.client_id}: {e}")
    
    async def _remove_client_by_id(self, client_id: str) -> None:
        """Удалить клиента по ID"""
        async with self._lock:
            pc_to_remove = None
            
            # Ищем в комнатах
            for room_id, connections in self.rooms.items():
                for pc in connections:
                    if hasattr(pc, 'client_id') and pc.client_id == client_id:
                        pc_to_remove = pc
                        break
                if pc_to_remove:
                    break
            
            # Ищем во временных
            if not pc_to_remove:
                for temp_id, pc in self.temporary_connections.items():
                    if hasattr(pc, 'client_id') and pc.client_id == client_id:
                        pc_to_remove = pc
                        break
            
            if pc_to_remove:
                await self._remove_client(pc_to_remove)
            else:
                logger.warning(f"Клиент {client_id} не найден для удаления")
