from typing import Optional

from app.infrastructure.adapters.services.webrtc_manager_impl import WebRTCManagerImpl
from app.infrastructure.storage.clickhouse_client import ClickHouseAsyncClient
from app.infrastructure.config.settings import settings


class WebRTCInitializer:
    
    def __init__(self):
        self.webrtc_manager: Optional[WebRTCManagerImpl] = None
        self.clickhouse_client: Optional[ClickHouseAsyncClient] = None
        self.is_initialized = False
    
    async def initialize(self) -> None:
        if self.is_initialized:
            return
        
        print("Инициализация WebRTC компонентов...", flush=True)
        
        try:
            self.clickhouse_client = ClickHouseAsyncClient()
            await self.clickhouse_client.initialize()
            
            await self.clickhouse_client.create_tables_if_not_exists()
            print("ClickHouse инициализирован", flush=True)
            
            self.webrtc_manager = WebRTCManagerImpl()
            print("WebRTC Manager инициализирован", flush=True)
            
            await self._initialize_vector_search()
            
            self.is_initialized = True
            print("Все компоненты WebRTC инициализированы", flush=True)
            
        except Exception as e:
            print(f"Ошибка инициализации WebRTC: {e}", flush=True)
            raise
    
    async def _initialize_vector_search(self) -> None:
        """Инициализация векторного поиска"""
        # Здесь можно загрузить предобученную модель эмбеддингов
        # или инициализировать другие компоненты
        pass
    
    async def shutdown(self) -> None:
        print("Завершение работы WebRTC компонентов...", flush=True)
        
        try:
            if self.webrtc_manager:
                await self.webrtc_manager.shutdown()
                print("WebRTC соединения закрыты", flush=True)
            
            if self.clickhouse_client:
                await self.clickhouse_client.close()
                print("ClickHouse соединение закрыто", flush=True)
            
            self.is_initialized = False
            print("WebRTC компоненты завершены", flush=True)
            
        except Exception as e:
            print(f"Ошибка при завершении WebRTC: {e}", flush=True)
    
    def get_webrtc_manager(self) -> WebRTCManagerImpl:
        if not self.webrtc_manager:
            raise RuntimeError("WebRTC Manager не инициализирован")
        return self.webrtc_manager
    
    def get_clickhouse_client(self) -> ClickHouseAsyncClient:
        if not self.clickhouse_client:
            raise RuntimeError("ClickHouse клиент не инициализирован")
        return self.clickhouse_client


_webrtc_initializer: Optional[WebRTCInitializer] = None

async def get_webrtc_initializer() -> WebRTCInitializer:
    global _webrtc_initializer
    
    if _webrtc_initializer is None:
        _webrtc_initializer = WebRTCInitializer()
        await _webrtc_initializer.initialize()
    
    return _webrtc_initializer
