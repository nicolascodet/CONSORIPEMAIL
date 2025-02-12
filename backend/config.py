import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    MS_CLIENT_ID: str
    MS_CLIENT_SECRET: str
    MS_TENANT_ID: str
    DATABASE_URL: str
    ATTACHMENT_STORAGE_PATH: str

    class Config:
        env_file = ".env"

settings = Settings()

# Create necessary directories
os.makedirs(settings.ATTACHMENT_STORAGE_PATH, exist_ok=True)
