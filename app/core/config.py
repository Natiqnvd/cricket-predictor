from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    APP_NAME: str = "Cricket Predictor"
    DEBUG: bool = False
    DATABASE_URL: PostgresDsn
    REDIS_URL: str
    SECRET_KEY: str

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        env_file_encoding = "utf-8"

settings = Settings()
