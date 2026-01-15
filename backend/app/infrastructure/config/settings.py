from pydantic_settings import BaseSettings


# TODO: вынести часть переменных в secrets.py
class Settings(BaseSettings):
    BACKEND_HOST: str
    BACKEND_PORT: int

    FASTAPI_HOST: str
    FASTAPI_PORT: int
    UVICORN_WORKERS: int = 1

    DB_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int

    SECRET_KEY: str = "asfdslknfsdfsdfjksdlkjfkjdsfjskjfsjdfndsfnkjfnskjfskjfskjfk"
    ALGORITHM: str = "HS256"

    COOKIE_NAME: str = "access_token"

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    class Config:
        env_file = ".env"


settings = Settings()
