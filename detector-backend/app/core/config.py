from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://mongo:27017"
    MONGO_DB_NAME: str = "fakenews"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
