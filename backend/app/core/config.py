from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    SECRET_KEY: str
    SPACES_KEY: str
    SPACES_SECRET: str
    SPACES_BUCKET: str
    SPACES_REGION: str
    SPACES_ENDPOINT: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

@lru_cache
def get_settings() -> Settings:
    return Settings()
