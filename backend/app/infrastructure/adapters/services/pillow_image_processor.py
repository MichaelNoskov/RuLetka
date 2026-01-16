import io
from PIL import Image
from typing import Tuple

from app.core.ports.services.image_processor import AbstractImageProcessor


class PillowImageProcessor(AbstractImageProcessor):
    
    def process_avatar(
        self, 
        image_bytes: bytes, 
        size: Tuple[int, int] = (256, 256),
        quality: int = 85
    ) -> bytes:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert('RGB')
            
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            
            return output.read()
        except Exception as e:
            raise ValueError("Ошибка обработки изображения")
