from minio import Minio
from minio.error import S3Error
from common.core.config import settings
from io import BytesIO


minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False,
)


async def upload_image(filename, image_bytes):
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET):
            minio_client.make_bucket(settings.MINIO_BUCKET)

        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET, object_name=filename, data=BytesIO(image_bytes), length=len(image_bytes)
        )
        print(f"File {filename} uploaded to bucket {settings.MINIO_BUCKET}.")

    except S3Error as e:
        print(f"Error occurred: {e}")
        return


async def get_image(filename):
    try:
        response = minio_client.get_object(settings.MINIO_BUCKET, filename)
        return response.read()
    except S3Error as e:
        print(f"Error occurred: {e}")