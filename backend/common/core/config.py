from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_PORT: int
    FASTAPI_PORT: int
    BACKEND_HOST: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    RABBIT_HOST: str
    RABBIT_PORT: int
    RABBIT_USER: str
    RABBIT_PASSWORD: str

    CLICKHOUSE_HOST: str
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DB: str
    CLICKHOUSE_HTTP_PORT: int
    CLICKHOUSE_TCP_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PASSWORD: str
    REDIS_POOL_MINSIZE: int = 5
    REDIS_POOL_MAXSIZE: int = 20
    REDIS_TIMEOUT: int = 5

    MINIO_PORT: int
    MINIO_API_PORT: int
    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET: str

    USER_QUEUE: str = 'user.{user_id}'
    DB_QUEUE: str = 'user_db_ask'
    MODEL_QUEUE: str = 'user_click_ask'

    SECRET_KEY: str = "asfdslknfsdfsdfjksdlkjfkjdsfjskjfsjdfndsfnkjfnskjfskjfskjfk"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    COOKIE_NAME: str = "access_token"
    
    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    @property
    def rabbit_url(self) -> str:
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}"
    
    @property
    def clickhouse_http_url(self) -> str:
        return f"http://{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_HTTP_PORT}"

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"


settings = Settings()