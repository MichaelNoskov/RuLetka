from pathlib import Path

from app.infrastructure.external.fs_static_file_loader import FileSystemStaticFileLoader
from app.infrastructure.config.settings import settings


class StaticResourceInitializer:
    @staticmethod
    def initialize():
        static_dir = Path(settings.STATIC_DIR)
        static_dir.mkdir(parents=True, exist_ok=True)

        default_avatar = static_dir / "default_avatar.jpg"
        if not default_avatar.exists():
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (256, 256), color='gray')
            draw = ImageDraw.Draw(img)
            draw.text((128, 128), "AVATAR", fill='white', anchor="mm")
            img.save(default_avatar)
        
        return FileSystemStaticFileLoader(str(static_dir))
