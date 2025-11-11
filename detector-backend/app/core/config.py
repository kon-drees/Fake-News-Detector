from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "fakenews"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
