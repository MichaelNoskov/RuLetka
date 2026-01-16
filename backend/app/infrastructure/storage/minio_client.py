from typing import Optional
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from app.infrastructure.config.settings import settings


class MinIOClient:
    def __init__(self):
        self._client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )
    
    def _ensure_bucket_exists(self, bucket: str) -> None:
        try:
            if not self._client.bucket_exists(bucket):
                self._client.make_bucket(bucket)
                print(f"Bucket '{bucket}' создан", flush=True)
        except S3Error as e:
            print(f"Не получилось найти или создать bucket", flush=True)
            raise
    
    async def save_file(self, filename: str, image_bytes: bytes, bucket: str) -> Optional[str]:
        try:
            self._client.put_object(
                bucket_name=bucket,
                object_name=filename,
                data=BytesIO(image_bytes),
                length=len(image_bytes),
            )

            print(f"Файл {filename} загружен в bucket {bucket}.", flush=True)
            return filename
            
        except S3Error as e:
            print(f"Произошла ошибка при загрузке файла", flush=True)
            return None
    
    async def get_file(self, filename: str, bucket: str) -> Optional[bytes]:
        try:
            response = self._client.get_object(bucket, filename)
            image_data = response.read()
            response.close()
            response.release_conn()
            return image_data
            
        except S3Error as e:
            print(f"Произошла ошибка при загрузке файла", flush=True)
            return None

    async def delete_file(self, filename: str, bucket: str) -> bool:
        try:
            self._client.remove_object(bucket, filename)
            print(f"Файл {filename} удалён из bucket {bucket}.", flush=True)
            return True
            
        except S3Error as e:
            print(f"Произошла ошибка при удалении файла", flush=True)
            return False
