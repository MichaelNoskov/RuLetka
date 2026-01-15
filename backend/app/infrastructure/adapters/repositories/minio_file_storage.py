from typing import Optional

from app.domain.ports.file_storage import AbstractFileStorage
from app.infrastructure.storage.minio_client import MinIOClient


class MinIOFileStorage(AbstractFileStorage):
    
    def __init__(self, bucket_name: str):
        self.client = MinIOClient()
        self.client._ensure_bucket_exists(bucket_name)
        self._bucket_name = bucket_name

    @property
    def bucket(self) -> str:
        return self._bucket_name
    
    async def save_file(self, filename: str, image_bytes: bytes) -> str:
        return await self.client.save_file(filename, image_bytes, self.bucket)
    
    async def get_file(self, filename: str) -> Optional[bytes]:
        return await self.client.get_file(filename, self.bucket)
