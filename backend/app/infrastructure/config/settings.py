from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_HOST: str
    BACKEND_PORT: int

    FASTAPI_HOST: str
    FASTAPI_PORT: int

    # TODO: вынести в secrets.py
    SECRET_KEY: str = "asfdslknfsdfsdfjksdlkjfkjdsfjskjfsjdfndsfnkjfnskjfskjfskjfk"
    ALGORITHM: str = "HS256"

    COOKIE_NAME: str = "access_token"

    class Config:
        env_file = ".env"


settings = Settings()
