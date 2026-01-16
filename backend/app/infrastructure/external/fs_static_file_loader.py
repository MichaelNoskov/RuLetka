import asyncio
from pathlib import Path
from typing import Optional
import os

from app.core.ports.services.static_file_loader import AbstractStaticFileLoader


class FileSystemStaticFileLoader(AbstractStaticFileLoader):
    
    def __init__(self, static_dir: str):
        self.static_dir = Path(static_dir)
    
    async def load_default_avatar(self) -> Optional[bytes]:
        avatar_path = self.static_dir / "default_avatar.jpg"
        
        if not os.path.exists(avatar_path):
            return None
        
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: avatar_path.read_bytes()
            )
            return data
        except Exception:
            return None
