from app.domain.ports.static_file_loader import AbstractStaticFileLoader
from app.domain.ports.file_storage import AbstractFileStorage


class StaticResourceInitializer:
    
    def __init__(
        self,
        static_loader: AbstractStaticFileLoader,
        file_storage: AbstractFileStorage
    ):
        self.static_loader = static_loader
        self.file_storage = file_storage
    
    async def initialize_default_avatar(self) -> bool:
        filename = self.get_default_avatar_filename()

        try:
            existing_file = await self.file_storage.get_file(filename)
            if existing_file:
                print(f"Дефолтный аватар уже существует в хранилище", flush=True)
                return True
        except Exception:
            pass

        avatar_bytes = await self.static_loader.load_default_avatar()
        
        try:
            await self.file_storage.save_file(filename, avatar_bytes)
            print(f"Дефолтный аватар сохранен как {filename}", flush=True)
            return True
        except Exception as e:
            print(f"Ошибка сохранения дефолтного аватара: {e}", flush=True)
            return False
    
    def get_default_avatar_filename(self) -> str:
        return "default_avatar.jpg"
