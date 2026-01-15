from pydantic_settings import BaseSettings


# TODO: вынести часть переменных в secrets.py
class Settings(BaseSettings):
    BACKEND_HOST: str = "backend"
    BACKEND_PORT: int = 8000

    FASTAPI_HOST: str = "localhost"
    FASTAPI_PORT: int = 8000
    UVICORN_WORKERS: int = 1

    DB_HOST: str = "localhost"
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_PORT: int = 5432

    HTTPS_ONLY: bool = False

    JWT_SECRET_KEY: str = "asfdslknfsdfsdfjksdlkjfkjdsfjskjfsjdfndsfnkjfnskjfskjfskjfk"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    COOKIE_NAME: str = "access_token"

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    class Config:
        env_file = ".env"


settings = Settings()
