import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./email_analyzer.db")
    
    # File storage settings
    upload_folder: str = os.getenv("UPLOAD_FOLDER", str(Path("./data/uploads").absolute()))
    attachment_storage_path: str = os.getenv("ATTACHMENT_STORAGE_PATH", str(Path("./data/attachments").absolute()))
    max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", 1024 * 1024 * 1024))  # 1GB max file size
    max_attachment_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list[str] = [".pst", ".mbox"]
    
    # OpenAI settings
    openai_api_key: str
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # CORS settings
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Create necessary directories
os.makedirs(settings.upload_folder, exist_ok=True)
os.makedirs(settings.attachment_storage_path, exist_ok=True)
