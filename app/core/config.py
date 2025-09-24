from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    APP_NAME: str = "Cricket Predictor"
    DEBUG: bool = False
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str


class Config:
    env_file = ".env"


settings = Settings()